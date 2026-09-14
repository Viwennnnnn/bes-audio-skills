# Float-to-device validation gates

## Validation ladder

Advance only after the earlier layer is explained:

1. Float checkpoint reproduces the frozen evaluation baseline.
2. Exported float graph matches the training graph on deterministic inputs.
3. Framework fake-quant/quantized model meets the predefined degradation gate.
4. Host fixed-point frontend and model match golden boundaries.
5. Target simulator/library matches the host fixed-point implementation.
6. Firmware fed identical PCM matches host scores, states, and trigger decisions.
7. Acoustic playback regression meets algorithm and product gates.

## Test vectors

Include zero, impulse, alternating extrema, constant low/high level, deterministic pseudo-random values, short/partial chunks, reset/replay, long silence, target, hard negative, ordinary speech, noise, and near-threshold examples. For streaming models, include sequences long enough to expose state drift and chunk-boundary differences.

Store raw input plus selected boundary outputs or hashes. Dumping every tensor for a large corpus is unnecessary; keep a small diagnostic golden set and corpus-level final metrics.

## Boundary comparison

Compare in execution order: PCM conditioning, each frontend stage, feature normalization, each model block/gate/cache, classifier/logit, probability/score, smoothing, and trigger state machine. Report integer range, saturation count, max/mean absolute error, suitable relative/cosine metrics, and the first failing boundary.

Use exact equality where implementations are meant to share integer arithmetic. Where kernels differ legitimately, predeclare tolerances based on downstream decision stability rather than relaxing them after failures.

## Operational metrics

Recompute the dev threshold/temporal rule for the quantized model and freeze it before test. Compare float and fixed:

- positive FRR;
- open-domain event FA/h using actual audio exposure;
- hard-negative trigger rate separately;
- score shift/ranking near threshold;
- trigger latency and repeated/duplicate triggers.

Do not use accuracy alone. Quantization acceptance is tied to the intended operating point.

## Resource and robustness gates

Measure release and worst-case builds. Confirm Flash, persistent and scratch RAM, stack watermark, cycles/frame, maximum inference time, power if required, watchdog/reset behavior, and concurrency with real audio/transport tasks. Exercise repeated init/close, reset after trigger, malformed sizes, long continuous input, and low/high PCM levels.

## Release evidence

The release record must connect checkpoint, quantization/export manifest, library, firmware, device, threshold, corpus, and test logs by immutable IDs/hashes. Mark partial states explicitly; a successful host test is not device alignment, and device alignment is not an acoustic product pass.
