# Device playback and serial regression

## Test tiers

Keep separate test tiers instead of forcing one corpus to serve every goal:

- fast daily regression: deterministic subset, fixed order, repeatable acoustic setup;
- focused diagnostic retest: failures plus controlled context/repetitions;
- full offline evaluation: complete frozen manifests and PC scores;
- formal release evaluation: broader licensed corpus and realistic environments.

Do not present a daily regression subset as the final product-quality estimate.

## Playback manifest

Each row should contain a stable ID, relative audio path, original source key, category, source dataset, duration, sequence index, reset policy, pre/post wait, and expected outcome. Validate every file is unique where required and decodable before starting.

Use relative paths for portable packages. Follow the operating system's default output device and volume unless the protocol fixes an endpoint. If audio is converted, keep originals, record conversion parameters, and hash both files.

For positive and confusing-phrase samples, independent playback with a declared decision window is often easiest to attribute. For natural speech/background, retain a continuous-stream mode to expose state and boundary failures; also support isolated diagnostic playback.

## Valid trigger parsing

Count an algorithm trigger only when the log provides an explicit KWS trigger event under the declared firmware protocol. When available, require:

- matching configured model;
- a trigger score attached to that event;
- score at or above the configured threshold.

Do not promote ordinary state messages, initialization lines, wake locks, periodic scores, low scores, or model-mismatched records to triggers. Compute `peak_score` only from valid trigger events. Preserve excluded events and raw serial bytes for debugging.

## Per-play result contract

Every successful playback produces exactly one result row per enabled device. Include playback/sample identity, device identity, model, threshold, attempt number, valid trigger flag/count/scores, first trigger frame, timestamps, inference timing, exclusion count, abnormal status, and whether it enters metrics.

Retain raw RX/TX and decoded logs. Do not write missing timing values as zero.

## Dual-device testing

Play each audio once through the shared speaker clock while collecting two independent serial sessions. Keep parsers, receive buffers, event windows, logs, thresholds, and model identities separate. Disallow the same port for both devices.

Use the same start/end/decision window for A and B. Produce device-level metrics and a comparison row with both/neither/A-only/B-only, conclusion agreement, and per-device score. If either serial path fails, pause the shared run, mark that attempt abnormal for both, and retry the same sample after manual reconnection. Do not silently skip or continue one device.

## Abnormal handling

Serial disconnects, parser/protocol mismatches, watchdogs, unexpected reboot, playback errors, or incomplete results are test-infrastructure abnormalities. Preserve the attempt but exclude it from FRR/FA denominators. Avoid automatic hardware reset or port switching unless the user explicitly requests those behaviors.

## Metadata required for a trustworthy run

Record model checkpoint hash, exported parameter hash/CRC, firmware and KWS library revisions, model structure, threshold and temporal trigger rule, frontend/AGC configuration, device IDs, test manifest hash, system volume, output endpoint, speaker distance/orientation, and software version.

If these are unavailable, the result can be exploratory but cannot prove a regression between builds.

## Initial regression reporting

First runs should establish baselines rather than invent pass/fail gates after seeing results. Report completion/ordering integrity, per-category/source FRR or trigger rate, open-domain event FA/h, hard-negative rate, abnormalities, and inference-time distributions. Define future gates from stable repeated baselines and product requirements.
