---
name: kws-quant-deploy
description: Quantize a trained streaming KWS model, export reproducible fixed-point artifacts, integrate them into MCU/DSP firmware, and validate float-to-fixed-to-device consistency. Use for PTQ/QAT, calibration, Q-format and scale design, C arrays or static libraries, operator golden vectors, memory/latency checks, or quantization deployment failures.
---

# KWS Quantization and Deployment

Treat deployment as a versioned numerical contract:

`checkpoint -> frozen frontend/model/trigger policy -> calibration -> quantized graph -> exported parameters -> host fixed-point reference -> target library -> firmware image -> device result`

Do not call a deployment verified merely because it compiles or triggers on one WAV. Prove artifact identity and numerical behavior before acoustic testing.

## Route the task

- For PTQ/QAT choice, calibration, scales, zero-points, Q formats, accumulators, activation ranges, and recurrent-state handling, read [references/quantization-contract.md](references/quantization-contract.md).
- For export packages, C arrays, static libraries, ABI, reproducibility metadata, host harnesses, and firmware integration, read [references/export-integration.md](references/export-integration.md).
- For float/fake-quant/fixed/board validation and release gates, read [references/validation-gates.md](references/validation-gates.md).
- For saturation, scale, frontend, state, ABI, stale-image, performance, and field failures, read [references/troubleshooting.md](references/troubleshooting.md).

Read only the references needed for the current task. For a full delivery, apply them in the order above.

## Required invariants

1. Freeze checkpoint, model graph, frontend, streaming state/reset behavior, and trigger policy before quantization. Record hashes and dimensions.
2. Keep an untouched evaluation set. Calibration data represents deployment ranges but does not replace dev/test and must not leak held-out speakers or sessions when isolation is claimed.
3. State the numerical rule for every boundary: dtype, real scale or Q format, zero-point, axis/granularity, clamp range, accumulator width, bias scale, requantization multiplier/shift, rounding, and saturation.
4. Quantize persistent streaming state explicitly. Reset/carry semantics and cache layout are part of the model contract.
5. Export from one canonical manifest. Generated headers, blobs, libraries, model metadata, and tests must agree on architecture, shapes, hashes, and version.
6. Validate the same inputs through float, fake-quant or quantized framework, host fixed-point C/C++, and target implementation. Compare the first divergent boundary rather than only the final score.
7. Re-sweep the dev operating point after quantization. Do not copy the float threshold blindly or tune on test/device failures.
8. A release requires numerical, algorithm, integration, resource, and on-device regression evidence. Exclude infrastructure abnormalities from algorithm metrics but preserve their logs.

## Working method

Start read-only: inventory checkpoints, exporters, quantization configs, generated artifacts, runtime sources, libraries, firmware images, and existing golden tests. Determine whether the implementation uses affine integers, symmetric integers, power-of-two Q formats, mixed precision, vendor kernels, or a combination; do not impose another scheme without a measured reason.

For changes, create a new versioned export directory and preserve the previous deployable baseline. Run a tiny deterministic smoke vector before a full corpus. Use `scripts/verify_deployment_manifest.py` to validate a deployment manifest and file hashes when the package follows the documented schema.

## Reporting

Lead with readiness: `not frozen`, `quantized but unverified`, `host-aligned`, `device-aligned`, or `release-qualified`. Report:

- source checkpoint and export manifest hashes;
- frontend/model/trigger versions and quantization method;
- calibration identity and coverage;
- per-boundary error, saturation/clipping, and first divergence;
- float versus fixed FRR, open-domain FA/h, and hard-negative rate at frozen operating points;
- Flash, peak/persistent RAM, stack, cycles/latency, and real-time margin;
- target firmware/library revision and on-device regression result;
- unresolved risks and the smallest test that separates likely causes.

Do not embed proprietary weights, audio, credentials, private hosts, or personal absolute paths in this skill or public reports.
