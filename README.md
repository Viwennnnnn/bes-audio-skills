# Codex BES Audio Skills

Reusable Codex skills distilled from BES1700 `main_v2` audio/KWS work.

| Skill | Use it for |
| --- | --- |
| `bes-audio-firmware-map` | Trace and explain G19 PAV/G28 RM1 audio firmware and algorithm paths |
| `bes-kws-port-build` | Identify, synchronize, build, and validate M33 KWS variants |
| `bes-gerrit-delivery` | Safely upload scoped changes from nested repositories to Gerrit |
| `bes-smf-log-debug` | Diagnose missing UART, SMF, VAD, and KWS logs |

Each child directory is a standalone skill. Install by copying or linking the desired directory into `~/.codex/skills/`.

Project-specific facts are explicitly marked as snapshots and should be revalidated against the active checkout.
