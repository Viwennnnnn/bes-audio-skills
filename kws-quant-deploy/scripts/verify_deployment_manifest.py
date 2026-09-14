#!/usr/bin/env python3
"""Validate a KWS deployment manifest and SHA-256 artifact identities."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any


REQUIRED_TOP_LEVEL = (
    "schema_version",
    "model_id",
    "architecture",
    "checkpoint_sha256",
    "frontend",
    "streaming",
    "quantization",
    "trigger",
    "artifacts",
)
REQUIRED_FRONTEND = ("sample_rate_hz", "frame_samples", "hop_samples", "feature_type")
REQUIRED_STREAMING = ("stateful", "reset_policy")
REQUIRED_QUANTIZATION = ("method", "weight_dtype", "activation_dtype", "rounding", "saturation")
REQUIRED_TRIGGER = ("score_domain", "threshold", "temporal_rule")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def missing_fields(value: Any, names: tuple[str, ...], prefix: str) -> list[str]:
    if not isinstance(value, dict):
        return [prefix.rstrip(".")]
    return [f"{prefix}{name}" for name in names if value.get(name) in (None, "")]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest", type=Path)
    parser.add_argument("--root", type=Path, help="Artifact root; defaults to manifest directory")
    args = parser.parse_args()

    manifest_path = args.manifest.resolve()
    root = (args.root.resolve() if args.root else manifest_path.parent)
    errors: list[str] = []
    try:
        document = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(json.dumps({"status": "FAIL", "errors": [str(exc)]}, indent=2))
        return 2
    if not isinstance(document, dict):
        errors.append("manifest root must be an object")
        document = {}

    errors.extend(missing_fields(document, REQUIRED_TOP_LEVEL, ""))
    errors.extend(missing_fields(document.get("frontend"), REQUIRED_FRONTEND, "frontend."))
    errors.extend(missing_fields(document.get("streaming"), REQUIRED_STREAMING, "streaming."))
    errors.extend(missing_fields(document.get("quantization"), REQUIRED_QUANTIZATION, "quantization."))
    errors.extend(missing_fields(document.get("trigger"), REQUIRED_TRIGGER, "trigger."))

    checkpoint_hash = str(document.get("checkpoint_sha256") or "").lower()
    if checkpoint_hash and (len(checkpoint_hash) != 64 or any(c not in "0123456789abcdef" for c in checkpoint_hash)):
        errors.append("checkpoint_sha256 must contain 64 hexadecimal characters")

    artifacts = document.get("artifacts")
    results: list[dict[str, Any]] = []
    if not isinstance(artifacts, list) or not artifacts:
        errors.append("artifacts must be a non-empty list")
    else:
        seen_names: set[str] = set()
        for index, artifact in enumerate(artifacts):
            if not isinstance(artifact, dict):
                errors.append(f"artifacts[{index}] must be an object")
                continue
            name = str(artifact.get("name") or "")
            relative = str(artifact.get("path") or "")
            expected = str(artifact.get("sha256") or "").lower()
            if not name or not relative or not expected:
                errors.append(f"artifacts[{index}] requires name, path, and sha256")
                continue
            if name in seen_names:
                errors.append(f"duplicate artifact name: {name}")
            seen_names.add(name)
            path = (root / relative).resolve()
            try:
                path.relative_to(root)
            except ValueError:
                errors.append(f"artifact escapes root: {relative}")
                continue
            if not path.is_file():
                errors.append(f"missing artifact: {relative}")
                continue
            actual = sha256(path)
            matched = actual == expected
            results.append({"name": name, "path": relative, "sha256": actual, "matched": matched})
            if not matched:
                errors.append(f"hash mismatch: {relative}")

    report = {"status": "PASS" if not errors else "FAIL", "manifest": str(manifest_path),
              "artifacts": results, "errors": errors}
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if not errors else 2


if __name__ == "__main__":
    sys.exit(main())
