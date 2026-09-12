---
name: audio-firmware-map
description: Inspect and explain embedded audio firmware paths, algorithm stages, core ownership, data formats, and product differences. Use for architecture walkthroughs and evidence-based capability comparisons, not for modifying or building firmware.
---

# Audio Firmware Map

Start from the selected product configuration, then trace references outward. Do not infer that a directory or library is active merely because it exists.

## Evidence and conventions

- Confirm which product/board variant is in scope; similarly named EVB, reference, and product configurations may differ.
- Distinguish audio cores and inter-core transport instead of attributing a feature to the whole firmware.
- Prefer evidence from board configuration, audio graph, build files, linked symbols, and final image strings over filenames or old backup artifacts.
- Do not infer that a directory, static library, or prebuilt binary is active merely because it exists.

## Workflow

1. Confirm the SDK root and target board from the user's workspace.
2. Inspect the target's audio/framework configuration and follow its graph/library references.
3. Identify capture source, sample format, buffers/shared memory, algorithm stages, consumers, and owning core.
4. Compare products by active topology and build configuration, not by recursively comparing whole directories.
5. Clearly label each result as active, compiled-but-not-used, prebuilt, placeholder, or unverified.

Read [references/project-context.md](references/project-context.md) only when the BES1700 case study is relevant.
