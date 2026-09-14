#!/usr/bin/env python3
"""Build an isolated repeated retest schedule from failed playback rows."""

from __future__ import annotations

import argparse
import csv
import json
import os
import sys
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--schedule", type=Path, required=True)
    parser.add_argument("--failures", type=Path, required=True,
                        help="CSV containing sequence_index for each target failure")
    parser.add_argument("--output-root", type=Path, required=True)
    parser.add_argument("--audio-root", type=Path,
                        help="Root used to resolve schedule audio paths; defaults to schedule grandparent")
    parser.add_argument("--neighbors", type=int, default=1)
    parser.add_argument("--repeats", type=int, default=5)
    parser.add_argument("--silence-ms", type=int, default=1000)
    args = parser.parse_args()
    if args.neighbors < 0 or args.repeats < 1 or args.silence_ms < 0:
        parser.error("neighbors/silence must be non-negative and repeats must be positive")

    schedule_path = args.schedule.resolve()
    failure_path = args.failures.resolve()
    output_root = args.output_root.resolve()
    audio_root = (args.audio_root or schedule_path.parent.parent).resolve()
    with schedule_path.open(encoding="utf-8-sig", newline="") as handle:
        schedule = list(csv.DictReader(handle))
    with failure_path.open(encoding="utf-8-sig", newline="") as handle:
        failures = list(csv.DictReader(handle))
    if not schedule or "sequence_index" not in schedule[0]:
        parser.error("schedule requires sequence_index")
    if not failures or "sequence_index" not in failures[0]:
        parser.error("failures requires sequence_index")

    by_sequence = {int(row["sequence_index"]): row for row in schedule}
    targets = {int(row["sequence_index"]) for row in failures}
    missing_targets = sorted(targets - set(by_sequence))
    if missing_targets:
        parser.error(f"failure sequence indices absent from schedule: {missing_targets[:10]}")
    selected: set[int] = set()
    for target in targets:
        selected.update(index for index in range(target - args.neighbors, target + args.neighbors + 1)
                        if index in by_sequence)

    playback_dir = output_root / "playback"
    manifests_dir = output_root / "manifests"
    playback_dir.mkdir(parents=True, exist_ok=True)
    manifests_dir.mkdir(parents=True, exist_ok=True)
    fields = list(schedule[0])
    if "wait_before_ms" not in fields:
        fields.insert(fields.index("reset_before") if "reset_before" in fields else len(fields), "wait_before_ms")
    rows: list[dict[str, str | int]] = []
    provenance: list[dict[str, object]] = []
    sequence = 0
    missing_audio: list[str] = []
    for original_sequence in sorted(selected):
        original = by_sequence[original_sequence]
        source_audio = (audio_root / original["audio_file"]).resolve()
        if not source_audio.is_file():
            missing_audio.append(str(source_audio))
        relative_audio = Path(os.path.relpath(source_audio, output_root)).as_posix()
        for repeat in range(1, args.repeats + 1):
            sequence += 1
            row: dict[str, str | int] = dict(original)
            row.update({
                "id": f"retest_{original_sequence:06d}_r{repeat}_{original['id']}",
                "audio_file": relative_audio, "sequence_index": sequence,
                "wait_before_ms": args.silence_ms, "reset_before": "True",
                "wait_after_ms": args.silence_ms,
            })
            rows.append(row)
            provenance.append({
                "retest_id": row["id"], "repeat": repeat,
                "original_id": original["id"], "original_sequence_index": original_sequence,
                "is_target_failure": original_sequence in targets,
                "distance_to_target": min(abs(original_sequence - target) for target in targets),
                "audio_file": relative_audio,
            })
    if missing_audio:
        print(json.dumps({"error": "missing audio", "examples": missing_audio[:20]}, indent=2), file=sys.stderr)
        return 2

    with (playback_dir / "playback_schedule.csv").open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)
    with (manifests_dir / "provenance.jsonl").open("w", encoding="utf-8") as handle:
        for row in provenance:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")
    plan = {
        "suite_type": "diagnostic_retest", "targets": len(targets),
        "unique_audio": len(selected), "repeats": args.repeats, "total_plays": len(rows),
        "neighbors_each_side": args.neighbors, "silence_before_after_ms": args.silence_ms,
        "stable_failure_suggestion": f"at least {(args.repeats // 2) + 1} of {args.repeats} repeats trigger",
    }
    (playback_dir / "playback_plan.json").write_text(
        json.dumps(plan, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(plan, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
