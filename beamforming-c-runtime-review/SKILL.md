---
name: beamforming-c-runtime-review
description: Review and hand off a two-microphone Beamforming C runtime layer by layer, from planar80 input and STFT through covariance, corrected MVDR, optional mask, iFFT/OLA, and DRC diagnostics.
---

# Beamforming C runtime review

Use this skill when reviewing the host-side reference implementation of the
two-microphone directional pickup algorithm. The host executable is a
source-logic reference; without Xtensa/NatureDSP it is not evidence of DSP
bit-exactness or on-device acoustic performance.

## Processing contract

- Input: 16 kHz, signed 16-bit, planar80 PCM. Each block is 80 samples of
  `mic0`, followed by 80 samples of `mic1` (320 bytes).
- Output: one mono signed-16-bit PCM block of 80 samples.
- Frame path: 256-sample history, Hann window, 256-point FFT, 129 non-negative
  bins, covariance EMA, MVDR weight update, complex frequency-domain multiply,
  real iFFT, and overlap-add.
- The current host reference enables the corrected MVDR covariance convention
  (`FX_MVDR_CONJ_COVARIANCE=1`) while retaining direct output `w^T x`.

For the complete layer-by-layer handoff map, read
[`references/flow.md`](references/flow.md).

## Review sequence

1. Run `make test` in the delivery package.
2. Convert a verified stereo 16 kHz WAV with `tools/run_one_wav.py`.
3. Listen to `bypass`, then pure `mvdr`, then `dsp_mask`. Treat
   `dsp_mask_drc` as diagnostic only; DRC changes level and is not currently a
   recommended spatial-processing path.
4. If results disagree, compare layers in this order: FFT snapshots, covariance
   values, MVDR weights, weighted spectrum, mask energy/ratio, iFFT/OLA, and
   finally DRC.
5. Use identical planar80 input for host and DSP comparisons. Confirm the
   physical left/right channel mapping with hardware before judging polarity.

## Interpretation boundaries

- A host self-test proves internal consistency, not NatureDSP intrinsic scales,
  FFT conventions, or hardware acoustics.
- Check the weight/output conjugation as one convention. A mismatch can produce
  a large audible failure even when individual fixed-point errors are small.
- Do not claim DSP equivalence until FFT, covariance, weights, and PCM output
  have been compared with the target toolchain or device golden vectors.

## Handoff checklist

- [ ] `make test` passes.
- [ ] Input layout and mic channel order are confirmed.
- [ ] Host and DSP use the same block boundaries and initialization.
- [ ] FFT and covariance are compared before MVDR weights.
- [ ] Pure MVDR is validated before enabling mask or DRC.
- [ ] Xtensa/NatureDSP versions and compiler options are recorded.
- [ ] Device PCM golden output is captured before claiming equivalence.
