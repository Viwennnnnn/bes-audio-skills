---
name: bes-audio-firmware-map
description: Inspect and explain audio firmware paths, algorithms, core ownership, and product differences in the BES1700 main_v2 SDK, especially G19 PAV and G28 RM1. Use for architecture walkthroughs and evidence-based capability comparisons, not for modifying or building firmware.
---

# BES Audio Firmware Map

Start from the selected product configuration, then trace references outward. Do not infer that a directory or library is active merely because it exists.

## Project conventions

- Treat `g19_pav` as the team's G19 product. Do not substitute `g19_evb`, which is the iFlytek/vendor variant.
- Treat `g28_rm1` as an early-stage translation product unless current code proves otherwise. It has no speaker and no call path, so AEC is normally out of scope.
- Distinguish the M33/BTH audio path from AP/M55 application behavior. KWS runs on M33/BTH in the examined configuration.
- Prefer evidence from the board config, SMF graph, Makefiles, linked symbols, and final image strings over filenames or old backup artifacts.

## Workflow

1. Confirm the SDK root and target board. Default known root: `/home/huangweiwen/work/sdk/bes1700_main_v2`.
2. Inspect the target's `metabounds/configs/<board>/multimedia/smf` configuration and follow its graph/library references.
3. Identify capture source, sample format, buffers/shared memory, algorithm stages, consumers, and owning core.
4. Compare products by active topology and build configuration, not by recursively comparing whole directories.
5. Clearly label each result as active, compiled-but-not-used, prebuilt, placeholder, or unverified.

Read [references/project-context.md](references/project-context.md) when comparing G19 PAV and G28 RM1 or advising what audio work belongs on G28.
