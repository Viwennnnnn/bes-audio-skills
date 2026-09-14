#!/usr/bin/env python3
"""Summarize KWS playback CSV results with explicit FRR and FA/h scopes."""

from __future__ import annotations

import argparse
import csv
import json
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any


TRUE_VALUES = {"1", "true", "yes", "y"}


def truth(value: Any) -> bool:
    return str(value or "").strip().lower() in TRUE_VALUES


def integer(value: Any, default: int = 0) -> int:
    try:
        return int(float(str(value)))
    except (TypeError, ValueError):
        return default


def number(value: Any) -> float | None:
    try:
        text = str(value).strip()
        return float(text) if text else None
    except (TypeError, ValueError):
        return None


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--schedule", type=Path, required=True)
    parser.add_argument("--results", type=Path, required=True)
    parser.add_argument("--output", type=Path, help="Write JSON summary")
    parser.add_argument("--open-domain", default="natural_speech,background",
                        help="Comma-separated categories counted in open-domain FA/h")
    parser.add_argument("--hard-negative", default="hard_negative",
                        help="Category reported separately from FA/h")
    parser.add_argument("--allow-incomplete", action="store_true",
                        help="Do not fail when scheduled rows have no result")
    parser.add_argument("--threshold", type=float,
                        help="When valid_triggered is absent, require peak_score >= this threshold")
    parser.add_argument("--model", help="Require result model/configured_model to match this value")
    args = parser.parse_args()

    with args.schedule.open(encoding="utf-8-sig", newline="") as handle:
        schedule = list(csv.DictReader(handle))
    with args.results.open(encoding="utf-8-sig", newline="") as handle:
        results = list(csv.DictReader(handle))
    if not schedule or not results:
        parser.error("schedule and results must be non-empty")

    by_id = {row["id"]: row for row in schedule}
    duplicate_ids = len(by_id) != len(schedule)
    result_ids = [row.get("id", "") for row in results]
    duplicate_result_ids = len(result_ids) != len(set(result_ids))
    open_domain = {item.strip() for item in args.open_domain.split(",") if item.strip()}
    grouped: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    unknown: list[str] = []
    valid_rows: list[dict[str, Any]] = []
    abnormalities = 0
    excluded_low_or_missing_score = 0
    model_mismatches = 0

    for row in results:
        sample = by_id.get(row.get("id", ""))
        if sample is None:
            unknown.append(row.get("id", ""))
            continue
        abnormal = truth(row.get("abnormal")) or bool(str(row.get("notes") or "").strip())
        include = not abnormal and ("include_in_metrics" not in row or truth(row.get("include_in_metrics")))
        if not include:
            abnormalities += 1
            continue
        merged = dict(sample)
        merged.update(row)
        result_model = str(row.get("configured_model") or row.get("model") or "").strip()
        if args.model and result_model.lower() != args.model.lower():
            model_mismatches += 1
            continue
        if "valid_triggered" in row:
            merged["_triggered"] = truth(row.get("valid_triggered"))
            merged["_events"] = integer(row.get("valid_trigger_count"), int(merged["_triggered"]))
        else:
            raw_triggered = truth(row.get("triggered"))
            score = number(row.get("trigger_score", row.get("peak_score")))
            score_valid = args.threshold is None or (score is not None and score >= args.threshold)
            merged["_triggered"] = raw_triggered and score_valid
            merged["_events"] = (integer(row.get("trigger_count"), 1)
                                  if merged["_triggered"] else 0)
            if raw_triggered and not score_valid:
                excluded_low_or_missing_score += 1
        try:
            merged["_duration_s"] = float(merged.get("actual_duration_s") or merged.get("duration_s") or 0)
        except ValueError:
            parser.error(f"invalid duration for {row.get('id')}")
        category = str(sample.get("category") or row.get("category") or "<missing>")
        source = str(sample.get("source_dataset") or row.get("source_dataset") or "<missing>")
        grouped[(category, source)].append(merged)
        valid_rows.append(merged)

    def base_stats(rows: list[dict[str, Any]]) -> dict[str, Any]:
        count = len(rows)
        triggered = sum(row["_triggered"] for row in rows)
        events = sum(row["_events"] for row in rows)
        hours = sum(row["_duration_s"] for row in rows) / 3600.0
        return {
            "files": count, "hours": hours, "triggered_files": triggered,
            "trigger_events": events,
            "file_trigger_rate": triggered / count if count else None,
        }

    def scoped_stats(category: str, rows: list[dict[str, Any]]) -> dict[str, Any]:
        result = base_stats(rows)
        if category == "positive":
            result["missed_files"] = result["files"] - result["triggered_files"]
            result["frr"] = result["missed_files"] / result["files"] if result["files"] else None
        elif category in open_domain:
            result["triggered_file_fa_per_hour"] = (
                result["triggered_files"] / result["hours"] if result["hours"] else None)
            result["event_fa_per_hour"] = (
                result["trigger_events"] / result["hours"] if result["hours"] else None)
        return result

    positive = [row for row in valid_rows if str(row.get("expected")) == "trigger"]
    positive_triggered = sum(row["_triggered"] for row in positive)
    open_rows = [row for row in valid_rows if str(row.get("category")) in open_domain]
    hard_rows = [row for row in valid_rows if str(row.get("category")) == args.hard_negative]
    missing_result_count = len(set(by_id) - set(result_ids))
    integrity_failed = (duplicate_ids or duplicate_result_ids or bool(unknown) or model_mismatches > 0
                        or (missing_result_count > 0 and not args.allow_incomplete))
    report = {
        "status": "FAIL" if integrity_failed else "PASS",
        "integrity": {
            "scheduled": len(schedule), "result_rows": len(results), "valid_rows": len(valid_rows),
            "abnormal_or_excluded": abnormalities, "duplicate_schedule_ids": duplicate_ids,
            "duplicate_result_ids": duplicate_result_ids,
            "unknown_result_ids": unknown[:20], "missing_result_count": missing_result_count,
            "model_mismatches": model_mismatches,
            "excluded_low_or_missing_score": excluded_low_or_missing_score,
        },
        "positive": {
            "files": len(positive), "triggered": positive_triggered,
            "missed": len(positive) - positive_triggered,
            "frr": (len(positive) - positive_triggered) / len(positive) if positive else None,
        },
        "open_domain": {"categories": sorted(open_domain), **base_stats(open_rows)},
        "hard_negative": {"category": args.hard_negative, **base_stats(hard_rows)},
        "by_category_source": {
            f"{category}/{source}": scoped_stats(category, rows)
            for (category, source), rows in sorted(grouped.items())
        },
        "metric_note": "Open-domain FA/h excludes hard negatives and uses scheduled audio duration.",
    }
    for key in ("triggered_file_fa_per_hour", "event_fa_per_hour"):
        report["open_domain"][key] = (
            report["open_domain"]["triggered_files" if key.startswith("triggered_file") else "trigger_events"]
            / report["open_domain"]["hours"] if report["open_domain"]["hours"] else None)
    output = json.dumps(report, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(output, encoding="utf-8")
    print(output, end="")
    return 0 if report["status"] == "PASS" else 2


if __name__ == "__main__":
    sys.exit(main())
