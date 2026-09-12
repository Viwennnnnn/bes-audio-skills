---
name: kws-port-build
description: Verify KWS model identity, port a known-good implementation between embedded targets, build the required firmware, and validate artifacts. Use for GRU/DS-TCN or other model-version checks, static-library migration, and cross-board integration.
---

# KWS Port and Build

Preserve a working algorithm unless the user explicitly asks to change it. Determine model identity from metadata, source configuration, library hashes, and symbols; never decide GRU versus DS-TCN from a filename alone.

## Invariants

- Confirm the source and destination targets explicitly; reference/EVB and product configurations can contain different algorithms.
- Identify which core owns KWS and whether the destination build embeds or coordinates that image; a component-only build may not validate the delivered product.
- Only synchronize the intended production files. Keep timestamped backups outside commits and exclude them from delivery.
- Verify hashes after copying a static library and compare headers/ABI together with the library.
- Preserve unrelated dirty-worktree changes.

## Port workflow

1. Read [references/g28-gru-v4.md](references/g28-gru-v4.md) only when using the included BES1700 case study.
2. Inspect Git status in the actual nested repository before editing; this SDK is a repo-style multi-repository checkout.
3. Record source and destination hashes and model metadata.
4. Synchronize only the agreed runtime source, public headers, and M33 static library.
5. Build at the scope requested, using the project's wrapper and dependency order rather than inventing per-core commands.
6. Confirm exit codes, final artifacts, timestamps, library/image strings, and resource usage. Warnings are not success; the build must return zero.
7. Report the exact model, build scope, output directory, and flashing manifest.

Run `scripts/audit_kws_sync.sh <sdk-root>` after a G19-to-G28 sync when available.
