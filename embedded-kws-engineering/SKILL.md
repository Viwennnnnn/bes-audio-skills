---
name: embedded-kws-engineering
description: Audit datasets, train and compare streaming keyword-spotting models, evaluate FRR and false alarms, diagnose PC-to-device mismatches, and build repeatable serial/audio regression tests for embedded KWS systems. Use for KWS data lineage, speaker/session isolation, model selection, thresholding, M-class MCU deployment validation, or failure-sample analysis; do not use for generic speech recognition projects.
---

# Embedded KWS Engineering

Treat a KWS result as a chain of evidence, not a single accuracy number:

`source audio -> lineage-safe split -> feature frontend -> model -> score/threshold policy -> deployment implementation -> acoustic playback -> serial parser -> report`

Locate the user's actual manifests, configs, checkpoints, logs, firmware metadata, and test outputs before drawing conclusions. Preserve historical artifacts and unrelated changes. Keep generated scripts, experiments, scores, and reports in purpose-specific directories rather than scattering them through the repository.

## Route the task

- For dataset inventory, label repair, leakage detection, or rebuilding a clean version, read [references/data-audit.md](references/data-audit.md).
- For model training, checkpoint selection, DET analysis, cross-validation, or augmentation, read [references/training-evaluation.md](references/training-evaluation.md).
- For playback automation, serial parsing, dual-device comparison, and release regression, read [references/device-regression.md](references/device-regression.md).
- For unexpectedly high FRR/FA, PC-versus-board disagreement, or failure-sample mining, read [references/failure-diagnosis.md](references/failure-diagnosis.md).
- For organizing a mature experimental workspace, archiving old work, or monitoring remote runs, read [references/project-operations.md](references/project-operations.md).

Read only the references needed for the current request. When the task spans data, training, and device testing, apply them in that order.

## Non-negotiable experimental invariants

1. Split original source families, speakers, and sessions before generating or selecting derivatives. Clean, speed, noise, RIR, EQ, codec, and device-rendered versions of one source belong to one split.
2. Keep train/dev/test roles explicit. Select checkpoints and thresholds on dev only. Freeze both before test and do not tune after seeing test results.
3. Report positive misses, open-domain false alarms, and confusing phrases separately. Do not convert hard-negative triggers into open-domain FA/h.
4. Use actual exposure duration for FA/h. Distinguish trigger events from triggered files and state which numerator is used.
5. Never use CV accuracy as the primary KWS selection metric. Report the operating point: threshold, FRR, FA/h, and hard-negative trigger rate.
6. Record enough provenance to reproduce every result: manifest/config/checkpoint hashes, frontend, model structure, threshold logic, code or firmware revision, device identity, and acoustic conditions.
7. If PC and device disagree, first verify the exact weight/export/firmware chain, then compare the same captured input layer by layer. Raising the threshold is not a diagnosis.
8. Treat decode errors, serial loss, watchdogs, resets, model-name mismatches, and incomplete playback as abnormal attempts excluded from algorithm metrics but retained in raw logs.

## Working method

Start with read-only discovery and produce an evidence inventory. State any assumption that changes the experimental interpretation. For changes, create versioned outputs without overwriting source data, historical checkpoints, frozen tests, or prior reports. Run proportional validation: manifest assertions for data work, training/evaluation smoke checks for model work, and synthetic parser plus executable-start tests for desktop tooling.

Prefer the supplied dependency-free helpers when their input format matches:

- `scripts/audit_kws_splits.py`: summarize JSONL manifests and detect cross-split path, hash, family, parent, or speaker overlap.
- `scripts/summarize_playback_results.py`: merge a playback schedule with per-play results and compute positive FRR plus separate negative trigger and FA/h statistics.
- `scripts/build_failure_retest.py`: create a focused retest schedule from failed sequence indices and their neighbors.

Inspect `--help` before use. Adapt a copy when the local schema differs; do not silently guess field meanings.

## Reporting

Lead with the decision and its evidence. Always distinguish observed facts from hypotheses and recommended next experiments. A useful report states:

- exactly which data, model, checkpoint, frontend, threshold, device, and test run were analyzed;
- sample counts and actual hours by split/category/source;
- FRR, event-level FA/h, sample trigger rate, hard-negative rate, and abnormal count;
- failure concentration by source/family/speaker/condition;
- what has been ruled out, what remains unverified, and the smallest next test that separates competing causes.

Do not embed credentials, private hostnames, personal absolute paths, or proprietary audio/model files in generated reports or in this skill.
