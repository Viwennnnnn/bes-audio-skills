# Quantization contract

## Freeze the deployable graph

Record the checkpoint hash, exact inference graph, input shape/rate, frontend constants, causal context, frame/hop size, output convention, recurrent/cache tensors, reset behavior, smoothing, cooldown, and trigger threshold policy. Remove training-only nodes and make operator fusion explicit before collecting ranges.

## Choose PTQ or QAT from evidence

- Start with PTQ when operators are supported and representative calibration preserves the required operating point.
- Move to QAT when PTQ loss concentrates in sensitive nonlinearities, recurrent state, depthwise layers, normalization, or narrow activation ranges and cannot be fixed without unacceptable clipping or precision.
- Prefer mixed precision for proven hotspots when target kernels and memory budgets allow it. Do not widen everything because one layer diverges.

## Calibration

Use representative deployment-domain audio covering target speech, confusing phrases, ordinary speech, background/noise/music, silence, near-clipping, low-level input, device EQ/AGC, and streaming transitions. Preserve family/speaker/session isolation. Record manifest hash, preprocessing, number and duration by category, collector code revision, and range method.

Inspect range stability as calibration grows. A tiny convenient set or training batches sampled without provenance are not a defensible calibration set. For percentile or histogram clipping, report the rule and saturation rate on calibration and frozen dev data.

## Numerical specification

For every tensor boundary record:

| Field | Required meaning |
| --- | --- |
| dtype | signed/unsigned width |
| scale/Q | affine real scale or binary-point position |
| zero-point | scalar or per-axis values |
| granularity | per-tensor, per-channel, per-gate, or other declared axis |
| clamp | integer min/max actually used |
| accumulator | width and overflow behavior |
| bias | dtype and relationship to input/weight scales |
| requantize | multiplier, shift, order of operations |
| rounding | nearest-away, nearest-even, truncation, or exact target rule |
| saturation | where clamping occurs |

Match the target kernel's arithmetic order. Algebraically equivalent float expressions need not be fixed-point equivalent.

## Frontend and nonlinearities

Frontend parity commonly dominates model parity. Freeze PCM scaling, DC removal/pre-emphasis, framing, window coefficients, FFT scaling at each stage, magnitude/power convention, mel matrix quantization, log approximation/floor, normalization, feature layout, and warm-up behavior.

For sigmoid, tanh, exp, reciprocal, sqrt, LayerNorm, or softmax, record whether the target uses LUT, polynomial, piecewise linear, CMSIS/vendor implementation, and its input/output Q format. Validate endpoints and saturation zones, not only typical values.

## Recurrent and streaming state

For GRU/LSTM/FSMN/TCN caches, specify gate order, packed weight layout, state dtype/scale, update equation ordering, initial state, reset/clean API, carry across chunks, cache length, and alignment. Track saturation and drift across long continuous sequences; a one-frame unit test cannot expose state accumulation errors.

## Quantization acceptance

Set gates before reviewing final test results. Use layer-appropriate absolute/relative error, cosine similarity where meaningful, score/ranking agreement, saturation rate, and operational FRR/FA limits. A good average tensor error can still flip a threshold decision; include samples close to the operating point.
