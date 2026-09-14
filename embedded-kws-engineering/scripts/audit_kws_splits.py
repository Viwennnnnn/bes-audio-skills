#!/usr/bin/env python3
"""Audit JSONL KWS manifests for distribution and cross-split leakage."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


DEFAULT_FIELDS = {
    "path": ("wav", "audio_file", "audio", "path", "wav_path"),
    "sha256": ("sha256", "audio_sha256", "wav_sha256"),
    "family": ("source_family_id", "family_id", "family"),
    "parent": ("parent_source_id", "parent_id", "source_id", "source_wav"),
    "speaker": ("speaker", "speaker_id", "spk", "voice", "session"),
    "category": ("category", "class", "sample_type", "data_type"),
    "source": ("source_dataset", "dataset", "source"),
    "duration": ("duration_s", "duration", "wav_duration"),
    "label": ("label", "target", "keyword_id"),
}


def first_value(row: dict[str, Any], names: tuple[str, ...]) -> Any:
    for name in names:
        value = row.get(name)
        if value is not None and str(value).strip() != "":
            return value
    return None


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def normalized_path(value: Any, manifest: Path) -> str | None:
    if value is None:
        return None
    path = Path(str(value)).expanduser()
    if not path.is_absolute():
        path = manifest.parent / path
    return os.path.normcase(os.path.abspath(path))


def parse_split(value: str) -> tuple[str, Path]:
    if "=" not in value:
        raise argparse.ArgumentTypeError("split must be NAME=PATH")
    name, path = value.split("=", 1)
    if not name.strip() or not path.strip():
        raise argparse.ArgumentTypeError("split must be NAME=PATH")
    return name.strip(), Path(path).expanduser().resolve()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--split", action="append", required=True, type=parse_split,
                        help="Manifest assignment such as train=manifests/train.jsonl; repeat per split")
    parser.add_argument("--hash-files", action="store_true",
                        help="Compute hashes for existing audio when no manifest hash is present")
    parser.add_argument("--audio-root", type=Path,
                        help="Resolve relative audio paths against this root instead of each manifest directory")
    parser.add_argument("--output", type=Path, help="Write the complete JSON report")
    parser.add_argument("--allow-overlap", action="append", default=[],
                        choices=("path", "sha256", "family", "parent", "speaker"),
                        help="Do not fail on this overlap type")
    args = parser.parse_args()

    split_names = [name for name, _ in args.split]
    if len(split_names) != len(set(split_names)):
        parser.error("split names must be unique")

    values: dict[str, dict[str, set[str]]] = {}
    summaries: dict[str, Any] = {}
    errors: list[str] = []
    label_by_sha: dict[str, set[str]] = defaultdict(set)

    for split, manifest in args.split:
        if not manifest.is_file():
            errors.append(f"missing manifest: {manifest}")
            continue
        fields = {name: set() for name in ("path", "sha256", "family", "parent", "speaker")}
        categories: Counter[str] = Counter()
        sources: Counter[str] = Counter()
        rows = 0
        hours = 0.0
        missing_audio = 0
        invalid_json = 0
        with manifest.open(encoding="utf-8-sig") as handle:
            for line_no, line in enumerate(handle, 1):
                if not line.strip():
                    continue
                try:
                    row = json.loads(line)
                except json.JSONDecodeError as exc:
                    invalid_json += 1
                    errors.append(f"{manifest}:{line_no}: invalid JSON: {exc}")
                    continue
                if not isinstance(row, dict):
                    errors.append(f"{manifest}:{line_no}: row is not an object")
                    continue
                rows += 1
                raw_path = first_value(row, DEFAULT_FIELDS["path"])
                path = normalized_path(raw_path, (args.audio_root.resolve() / "manifest.jsonl") if args.audio_root else manifest)
                if path:
                    fields["path"].add(path)
                    if not Path(path).is_file():
                        missing_audio += 1
                sha = first_value(row, DEFAULT_FIELDS["sha256"])
                if not sha and args.hash_files and path and Path(path).is_file():
                    sha = file_sha256(Path(path))
                for key in ("family", "parent", "speaker"):
                    value = first_value(row, DEFAULT_FIELDS[key])
                    if value is not None:
                        fields[key].add(str(value))
                if sha:
                    sha_text = str(sha).lower()
                    fields["sha256"].add(sha_text)
                    label = first_value(row, DEFAULT_FIELDS["label"])
                    if label is not None:
                        label_by_sha[sha_text].add(str(label))
                category = first_value(row, DEFAULT_FIELDS["category"])
                source = first_value(row, DEFAULT_FIELDS["source"])
                categories[str(category) if category is not None else "<missing>"] += 1
                sources[str(source) if source is not None else "<missing>"] += 1
                duration = first_value(row, DEFAULT_FIELDS["duration"])
                if duration is not None:
                    try:
                        hours += float(duration) / 3600.0
                    except (TypeError, ValueError):
                        errors.append(f"{manifest}:{line_no}: invalid duration {duration!r}")
        values[split] = fields
        summaries[split] = {
            "manifest": str(manifest), "rows": rows, "hours": hours,
            "missing_audio": missing_audio, "invalid_json": invalid_json,
            "categories": dict(categories), "sources": dict(sources),
            "unique": {name: len(items) for name, items in fields.items()},
        }
        if missing_audio:
            errors.append(f"{manifest}: {missing_audio} referenced audio files are missing")

    overlaps: list[dict[str, Any]] = []
    names = list(values)
    for left_index, left in enumerate(names):
        for right in names[left_index + 1:]:
            for kind in ("path", "sha256", "family", "parent", "speaker"):
                common = values[left][kind] & values[right][kind]
                if common:
                    overlaps.append({
                        "left": left, "right": right, "kind": kind,
                        "count": len(common), "examples": sorted(common)[:10],
                        "allowed": kind in args.allow_overlap,
                    })

    label_conflicts = [
        {"sha256": sha, "labels": sorted(labels)}
        for sha, labels in label_by_sha.items() if len(labels) > 1
    ]
    blocking = [item for item in overlaps if not item["allowed"]]
    status = "PASS" if not errors and not blocking and not label_conflicts else "FAIL"
    report = {
        "status": status, "splits": summaries, "overlaps": overlaps,
        "label_conflicts": label_conflicts, "errors": errors,
        "notes": [
            "Only populated manifest fields are audited.",
            "Acoustic near-duplicate detection requires a project-specific fingerprinting stage.",
        ],
    }
    output = json.dumps(report, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(output, encoding="utf-8")
    print(output, end="")
    return 0 if status == "PASS" else 2


if __name__ == "__main__":
    sys.exit(main())
