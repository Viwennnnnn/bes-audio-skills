from __future__ import annotations

import csv
import json
import shutil
import subprocess
import sys
import unittest
import uuid
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
TEST_TMP = ROOT / ".test_tmp"
TEST_TMP.mkdir(exist_ok=True)


class WritableDirectory:
    def __enter__(self) -> Path:
        self.path = TEST_TMP / str(uuid.uuid4())
        self.path.mkdir()
        return self.path

    def __exit__(self, *_: object) -> None:
        shutil.rmtree(self.path, ignore_errors=True)


def run_script(name: str, *args: object) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPTS / name), *(str(arg) for arg in args)],
        text=True, capture_output=True, check=False,
    )


class SkillScriptTests(unittest.TestCase):
    def test_split_audit_rejects_family_overlap(self) -> None:
        with WritableDirectory() as root:
            audio = root / "audio"
            audio.mkdir()
            (audio / "a.wav").write_bytes(b"a")
            (audio / "b.wav").write_bytes(b"b")
            train = root / "train.jsonl"
            dev = root / "dev.jsonl"
            train.write_text(json.dumps({"audio_file": "audio/a.wav", "source_family_id": "same"}) + "\n")
            dev.write_text(json.dumps({"audio_file": "audio/b.wav", "source_family_id": "same"}) + "\n")
            result = run_script("audit_kws_splits.py", "--split", f"train={train}", "--split", f"dev={dev}")
            self.assertEqual(result.returncode, 2)
            payload = json.loads(result.stdout)
            self.assertEqual(payload["status"], "FAIL")
            self.assertEqual(payload["overlaps"][0]["kind"], "family")

    def test_summary_separates_open_domain_and_hard_negative(self) -> None:
        with WritableDirectory() as root:
            schedule = root / "schedule.csv"
            results = root / "results.csv"
            schedule_rows = [
                {"id": "p1", "category": "positive", "source_dataset": "pos", "duration_s": "1", "expected": "trigger"},
                {"id": "p2", "category": "positive", "source_dataset": "pos", "duration_s": "1", "expected": "trigger"},
                {"id": "n1", "category": "natural_speech", "source_dataset": "speech", "duration_s": "1800", "expected": "no_trigger"},
                {"id": "n2", "category": "background", "source_dataset": "noise", "duration_s": "1800", "expected": "no_trigger"},
                {"id": "h1", "category": "hard_negative", "source_dataset": "near", "duration_s": "10", "expected": "no_trigger"},
            ]
            result_rows = [
                {"id": "p1", "model": "gru", "triggered": "1", "trigger_count": "1", "peak_score": "0.8", "notes": ""},
                {"id": "p2", "model": "gru", "triggered": "1", "trigger_count": "1", "peak_score": "0.4", "notes": ""},
                {"id": "n1", "model": "gru", "triggered": "1", "trigger_count": "2", "peak_score": "0.9", "notes": ""},
                {"id": "n2", "model": "gru", "triggered": "0", "trigger_count": "0", "peak_score": "", "notes": ""},
                {"id": "h1", "model": "gru", "triggered": "1", "trigger_count": "1", "peak_score": "0.95", "notes": ""},
            ]
            for path, rows in ((schedule, schedule_rows), (results, result_rows)):
                with path.open("w", encoding="utf-8", newline="") as handle:
                    writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
                    writer.writeheader()
                    writer.writerows(rows)
            result = run_script("summarize_playback_results.py", "--schedule", schedule,
                                "--results", results, "--threshold", "0.72", "--model", "gru")
            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(result.stdout)
            self.assertEqual(payload["positive"]["frr"], 0.5)
            self.assertEqual(payload["open_domain"]["event_fa_per_hour"], 2.0)
            self.assertEqual(payload["hard_negative"]["triggered_files"], 1)
            self.assertNotIn("event_fa_per_hour", payload["hard_negative"])

    def test_failure_retest_selects_neighbors_and_repeats(self) -> None:
        with WritableDirectory() as root:
            audio = root / "audio"
            audio.mkdir()
            schedule = root / "playback" / "schedule.csv"
            schedule.parent.mkdir()
            rows = []
            for index in range(1, 6):
                (audio / f"{index}.wav").write_bytes(bytes([index]))
                rows.append({
                    "id": f"x{index}", "audio_file": f"audio/{index}.wav",
                    "sequence_index": index, "category": "natural_speech",
                    "source_dataset": "speech", "duration_s": 1,
                    "reset_before": "False", "wait_after_ms": 0, "expected": "no_trigger",
                })
            with schedule.open("w", encoding="utf-8", newline="") as handle:
                writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
                writer.writeheader()
                writer.writerows(rows)
            failures = root / "failures.csv"
            failures.write_text("sequence_index\n3\n", encoding="utf-8")
            output = root / "out"
            result = run_script("build_failure_retest.py", "--schedule", schedule,
                                "--failures", failures, "--output-root", output,
                                "--audio-root", root, "--repeats", "5")
            self.assertEqual(result.returncode, 0, result.stderr)
            with (output / "playback" / "playback_schedule.csv").open(encoding="utf-8-sig", newline="") as handle:
                retest = list(csv.DictReader(handle))
            self.assertEqual(len(retest), 15)
            self.assertEqual({row["wait_before_ms"] for row in retest}, {"1000"})
            self.assertEqual(len({row["id"] for row in retest}), 15)


if __name__ == "__main__":
    unittest.main()
