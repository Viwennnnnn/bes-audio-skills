---
name: bes-smf-log-debug
description: Diagnose missing UART output and SMF/KWS logs in BES1700 firmware by separating compile-time inclusion, runtime pipeline activation, log-level filtering, and flashing mistakes. Use when logs stop, show OFF, or expected VAD/KWS score lines are absent.
---

# BES SMF Log Debug

Do not immediately modify working algorithm code. Establish which of four layers failed: code inclusion, image delivery, runtime activation, or log routing/filtering.

## Diagnostic order

1. Inspect the source log calls and compile-time guards.
2. Search the relevant final M33/BTH binary with `strings` for distinctive format strings.
3. Verify that the flashed manifest actually carries or embeds the rebuilt M33 image and compare timestamps/hashes.
4. Confirm the VAD/KWS SMF node is instantiated. Absence of the initialization line after logs are enabled suggests the pipeline never opened.
5. Inspect the runtime log state and level. `SMF_LIBS_LOG_TEST` output may be compiled in but filtered until the corresponding UART/log service command enables it.

Read [references/kws-log-signatures.md](references/kws-log-signatures.md) for the current G28 GRU v4 signatures and interpretation.

Never invent a UART command syntax. Derive it from the running firmware's help/query output or source. If the console reports `Switch to OFF`, state confidently that output is disabled, but obtain the exact ON command from that firmware variant before advising transmission.
