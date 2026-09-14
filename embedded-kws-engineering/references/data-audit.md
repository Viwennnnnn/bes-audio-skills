# Dataset audit and rebuild

Use this workflow when historical manifests, generated aliases, TTS data, real recordings, or offline augmentations may contain bad labels, broken lineage, or leakage.

## Build an immutable asset registry

Treat old manifests as candidate inventories, not truth. For each asset, record when available:

- stable asset ID, current path, original path or alias, SHA-256;
- decode status, sample rate, channels, bit depth, duration;
- loudness/RMS, sample peak, clipping ratio, near-silence ratio, effective speech duration;
- label, transcript, category, source dataset, generator/voice/speaker/session;
- original source ID, `source_family_id`, `parent_source_id`, and ordered augmentation recipe;
- automated checks, human-review status, quarantine reason, and reviewer evidence.

Do not move or modify raw audio merely to make the registry tidy. Manifests may point to verified source files when obsolete aliases are missing.

## Define family identity before splitting

The family is the unit that must not cross splits. Group all derivatives of one source, including speed, noise, RIR, device, gain, EQ, codec, segmentation, and format conversion. For TTS, use the strongest available identity from transcript, engine, voice, generation recipe, and source metadata. Do not infer equivalence only from similar basenames.

Check leakage at multiple levels:

1. normalized/canonical path;
2. exact file SHA-256;
3. original source and parent ID;
4. source family;
5. speaker/session or TTS voice group when isolation is required;
6. acoustic near-duplicate cluster when available.

Any cross-label exact duplicate is a blocking conflict. A cross-split family/source/speaker overlap is blocking when the experiment claims isolation.

## Label and quality policy

- Use generation records or reviewed transcripts as the primary truth for synthetic speech.
- Use ASR only as a triage signal unless the protocol explicitly accepts it as ground truth.
- Require human listening evidence before admitting uncertain real positive recordings to a strict training set.
- Quarantine context-containing targets, uncertain pronunciation, decode failures, severe clipping/silence, label conflicts, and unverifiable lineage.
- A rejected positive does not automatically become a negative. Only confirmed non-target speech may enter a negative candidate pool.
- Keep real external-evaluation speakers entirely out of pretraining manifests.

## Rebuild procedure

1. Inventory all candidate manifests and storage roots.
2. Resolve aliases to sources using metadata and hashes; never guess missing files by basename alone.
3. Create the asset and family registries.
4. Apply quality/label gates and write quarantine references with reasons.
5. Stratify and assign families to train/dev/test according to the requested fixed sizes or ratios.
6. Generate manifests only from the fixed family mapping.
7. Generate offline training derivatives only from training families.
8. Run overlap, missing-file, duplicate-weight, label-conflict, and forbidden-path checks.
9. Hash registries, manifests, configs, and audit scripts.

When fixed split sizes imply ratios different from an earlier design, report the realized ratios exactly. Family isolation is more important than pretending an unattained ratio was used.

## Distribution report

Report counts and hours by split, class, source, engine/voice, speaker/session, duration bin, and augmentation recipe. Include accepted, quarantined, and rejected counts by reason. State which categories are real, synthetic, dry, or derived.

For positive and hard-negative phrases, preserve recoverable transcripts. If a legacy manifest contains only a generic filler token, report that phrase-level analysis is unavailable instead of fabricating labels.

## Acceptance gate

Do not mark a dataset trainable if any required invariant fails. The report must clearly separate historical reference results from results on an audited rebuild; they are not strict apples-to-apples comparisons when data or provenance changed.
