# Embedded Audio Firmware Skills

Reusable skills for embedded audio firmware investigation, KWS integration,
build validation, logging diagnosis, and Gerrit delivery. The original BES1700
work is retained as a concrete case study, but the workflows are intended to
apply to other vendors, boards, RTOSes, and repository layouts.

| Skill | Use it for |
| --- | --- |
| `audio-firmware-map` | Trace and explain embedded audio firmware and algorithm paths |
| `embedded-kws-engineering` | Audit data, train/fine-tune, evaluate, and debug embedded KWS systems |
| `kws-port-build` | Identify, synchronize, build, and validate KWS model variants |
| `gerrit-delivery` | Safely upload scoped changes from nested repositories to Gerrit |
| `smf-log-debug` | Diagnose missing UART, framework, VAD, and KWS logs |

Each child directory is a standalone skill. Install by copying or linking the desired directory into `~/.codex/skills/`.

Vendor- and project-specific facts are explicitly marked as snapshots and
should be revalidated against the active checkout.
