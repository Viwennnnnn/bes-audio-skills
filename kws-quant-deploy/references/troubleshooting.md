# Quantization and deployment troubleshooting

Use the earliest-divergence principle. Confirm measurement and artifact identity before changing scales, model, or threshold.

| Symptom | Likely checks | Corrective direction |
| --- | --- | --- |
| Fake-quant already degrades badly | calibration coverage, unsupported ops, activation outliers, normalization/nonlinearities | fix ranges/operator mapping; use QAT or targeted mixed precision only after localization |
| Host fixed differs from framework quantized | rounding, clamp order, multiplier/shift, bias scale, per-channel axis, fused-op order | make arithmetic contract explicit and add boundary golden vectors |
| Only board differs from host fixed | stale/wrong weights, ABI/layout, endianness, compiler UB, vendor kernel semantics, cache/state | prove image/library identity; bisect the same PCM boundary by boundary |
| Scores match after reset but drift in streams | state Q scale, saturation, cache length/layout, reset/carry semantics, chunking | log state ranges over long sequences and align update/reset order |
| Silence produces large features/scores | PCM sign/channel/bit-depth, DC/pre-emphasis, FFT scale, log floor, zero-point | test zero/constant vectors and fix frontend contract |
| One layer saturates heavily | bad calibration, wrong scale axis, overly narrow activation/state dtype | inspect real ranges; recalibrate or widen only the proven hotspot |
| Random large errors or build-dependent output | accumulator overflow, signed shift/overflow UB, alignment, uninitialized scratch/state | use wider intermediates, defined arithmetic helpers, sanitizers/host harness, explicit init |
| Model works on file but not microphone | acoustic domain, AGC/gain, sample format/rate, framing, device EQ/noise | capture device-domain PCM and run the same-input ladder |
| Firmware contains old behavior | wrong nested repo/config, library not relinked, embedded core image stale, wrong flash manifest/partition | inspect map/symbols/strings/hashes/timestamps and rebuild dependency chain |
| Compile/link failure after library replacement | ABI/header mismatch, missing runtime symbols, ISA/FPU flags, C/C++ linkage | compare exported symbols and headers; rebuild with compatible toolchain/options |
| RAM/latency regression | hidden scratch/heap, wider tensors, unfused copies, wrong kernel, logging overhead | measure per-stage memory/cycles and optimize the dominant stage |
| FRR/FA shifts but tensors are aligned | quantization genuinely changed score distribution or threshold policy differs | resweep dev operating point; verify smoothing/cooldown; do not tune test |
| Intermittent trigger attribution | serial loss, playback boundary, asynchronous logs, persistent state | preserve raw logs, isolate playback, repeat failures and neighbors, separate abnormalities |

## Minimum diagnostic bundle

Collect one failing input, float/fake-quant/host-fixed/device outputs, selected intermediate boundaries, quantization table, checkpoint/export/library/firmware hashes, build map, frontend/trigger configuration, reset/chunk sequence, and raw device logs. Without this bundle, label conclusions as hypotheses.

## Fix verification

After a fix, rerun the smallest reproducer, boundary golden set, frozen dev operating-point evaluation, resource checks, and affected device regression. Avoid claiming success from the reproducer alone.
