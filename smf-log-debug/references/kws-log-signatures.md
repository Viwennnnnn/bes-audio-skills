# Case study: G28 GRU v4 KWS log signatures

The examined `vad_algo.cpp` defaults to:

- `MJ_KWS_DEBUG_ENABLE=1`
- `MJ_KWS_AGC_ENABLE=1`
- `MJ_KWS_MODEL_NAME="gru"`
- one periodic diagnostic every 50 processed frames

Logging is routed through `vad_printf_test`, which calls `_libs.log(SMF_LIBS_LOG_TEST, ...)`. Therefore these messages can exist in the M33 image without appearing on UART when TEST/SMF logs are disabled.

Expected signatures include:

```text
[vad][gru] init ok, frame_len=...
[vad][gru] run frame=50 score=... state=... pcm_peak=... agc_peak=...
[vad][gru] trigger score=... state=...
```

Interpretation:

- Format strings absent from `nuttx_bth.bin`/`bth_core.bin`: wrong source, build option, or stale M33 build.
- Strings present but no init line after enabling TEST logs: VAD/KWS component likely was not opened.
- Init appears but no periodic run line: no frames are reaching the node, processing stopped early, or fewer than 50 frames elapsed.
- Run lines appear but no trigger: inspect score, PCM peak, AGC peak, threshold, model/audio format, and acoustic conditions.
- `me=base_svc_log_offline`, `query_cmd=6`, followed by `LOGS]:Switch to OFF`: the log service was explicitly switched off; this is a runtime filter state, not proof the KWS code is missing.

Useful binary check:

```bash
strings framework/services/out/bth_core/bth_core.bin |
  rg '\[vad\].*(init ok|run frame|trigger)'
```
