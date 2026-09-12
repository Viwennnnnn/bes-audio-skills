# Case study: G19 PAV and G28 RM1 audio context

This is a maintained BES1700 project snapshot, not a universal rule and not a substitute for inspecting the current checkout. Use it as an example of how to record product-specific evidence.

## Product intent

- G19 PAV is the team's G19 development target. G19 EVB belongs to the iFlytek/vendor line.
- G28 RM1 is a translation-oriented device: capture speech, send it to cloud ASR and translation, and consume the result. There is no speaker and no call requirement in the stated product scope.
- Therefore G28 front-end priorities are capture stability, channel correctness, gain consistency, clipping control, wind/mechanical-noise handling, speech/VAD segmentation, transport continuity, latency, and observability.
- AEC is not useful without a local playback reference. WebRTC's full voice-call stack is not the default fit; selectively evaluating portable APM components is more sensible.
- Traditional beamforming followed by ANS can help directional ASR when microphone geometry and steering assumptions are valid. Validate with ASR metrics and real noise scenes, not only SNR.

## Examined implementation state

- KWS is hosted on M33/BTH for both G19 PAV and G28 RM1.
- G28 initially appeared closer to driver/path bring-up than a mature front-end algorithm stack.
- The G28 SMF VAD/KWS node consumes 16 kHz, mono, 16-bit audio in the examined graph.
- Do not equate prebuilt DLLs, unused source folders, or backup files with an enabled runtime algorithm.

## Useful inspection targets

- `metabounds/configs/g19_pav/multimedia/smf/`
- `metabounds/configs/g28_rm1/multimedia/smf/`
- `metabounds/configs/<board>/multimedia/smf/smf.json`
- `metabounds/configs/<board>/multimedia/smf/vad_v3/`
- `framework/services/out/bth_core/bth_core.bin`
- `rtos/nuttx/nuttx_bth.bin`

For each feature, report: entry point, core, input format, algorithm/library, activation condition, output/event, and confidence/evidence.
