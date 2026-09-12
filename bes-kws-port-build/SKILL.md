---
name: bes-kws-port-build
description: Verify KWS model identity, synchronize the G19 PAV M33/BTH KWS implementation to another BES1700 product, build the required firmware, and validate artifacts. Use for GRU/DS-TCN version checks, static-library migration, and G28 RM1 builds.
---

# BES KWS Port and Build

Preserve a working algorithm unless the user explicitly asks to change it. Determine model identity from metadata, source configuration, library hashes, and symbols; never decide GRU versus DS-TCN from a filename alone.

## Invariants

- `g19_pav` is the source product when the user says the team's G19; never silently use `g19_evb`.
- KWS work is centered on M33/BTH, but a product switch to `g28_rm1` requires a full firmware build when requested because AP embeds/coordinates the M33 image.
- Only synchronize the intended production files. Keep timestamped backups outside commits and exclude them from delivery.
- Verify hashes after copying a static library and compare headers/ABI together with the library.
- Preserve unrelated dirty-worktree changes.

## Port workflow

1. Read [references/g28-gru-v4.md](references/g28-gru-v4.md) for the known baseline and file set.
2. Inspect Git status in the actual nested repository before editing; this SDK is a repo-style multi-repository checkout.
3. Record source and destination hashes and model metadata.
4. Synchronize only the agreed runtime source, public headers, and M33 static library.
5. Build at the scope requested. For G28 full firmware, use the project wrapper rather than inventing per-core commands.
6. Confirm exit codes, final artifacts, timestamps, library/image strings, and resource usage. Warnings are not success; the build must return zero.
7. Report the exact model, build scope, output directory, and flashing manifest.

Run `scripts/audit_kws_sync.sh <sdk-root>` after a G19-to-G28 sync when available.
