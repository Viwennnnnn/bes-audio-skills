# Failure diagnosis

Use this order when FRR or ordinary-negative false alarms look implausible.

## Validate the measurement first

1. Confirm the run is complete and identify missing categories/sources.
2. Recompute durations from decodable media where metadata contains placeholders; variable-length compressed files are a common source of bad FA/h.
3. Reparse raw logs using only valid explicit trigger events and the configured threshold.
4. Separate files triggered from trigger-event count.
5. Exclude abnormalities without deleting their evidence.
6. Confirm local audio hashes against the source manifest.

Never hide blank or below-threshold scores by turning them into zeros. State clearly whether a table is event-level, file-level, or score-distribution analysis.

## Localize concentration

Break failures down by class, source dataset, parent family, speaker/sex/session, transcript or confusing phrase, duration, loudness, augmentation recipe, and playback neighborhood. A high aggregate rate may be one broken family, one bad duration field, or a genuine broad-domain failure.

Do not overstate a category: a few augmented music/noise failures do not prove that all pure background noise fails.

## Verify artifact identity

Before changing training or threshold, record and compare:

- training checkpoint SHA-256;
- exported weights/quantized blob SHA or device CRC;
- model architecture and tensor dimensions;
- firmware/library revision;
- frontend and normalization constants;
- threshold representation, sigmoid/logit convention, smoothing, cooldown, and multi-frame rule;
- microphone, AGC, PCM format, and frame/cache behavior.

A GUI-selected model name is not proof of what is actually burned into the device.

## Focused reproducibility test

Build a small set from each valid false trigger plus its immediate predecessor and successor. Play each independently several times with fixed silence and setup. A useful initial rule is stable failure when at least 3 of 5 repeats trigger.

- Stable target: prioritize acoustic-domain or PC/device computation alignment.
- Target no longer stable: prioritize continuous-state, boundary attribution, or serial-window timing.
- Neighbor also stable: inspect the broader source/family and acoustic segment.

Do not immediately feed every one-off failure back into training.

## Same-input ladder

Capture the PCM that actually reaches the device and compare:

1. original test file -> PC float model;
2. captured device-domain PCM -> PC float model;
3. identical PCM/features -> device fixed-point implementation.

Interpretation:

| Observation | Primary suspect |
|---|---|
| Original file rejects; captured PCM triggers on PC | speaker/microphone/room/AGC acoustic domain |
| Captured PCM rejects on PC; device triggers | frontend, quantization, operator, threshold, or wrong weights |
| Both trigger on identical PCM | actual model weakness/hard sample |

For the third case, compare frame by frame: waveform framing/STFT, mel/log floor, normalization or LayerNorm, each recurrent/convolutional block, classifier logit, sigmoid/score, and trigger state machine. Report the first layer where error exceeds an agreed tolerance.

## Threshold and temporal logic

Produce a threshold tradeoff table before recommending changes. If a small threshold increase sharply harms FRR while FA remains high, threshold tuning cannot solve the problem. Multi-frame confirmation or VAD gating can suppress isolated spikes, but first inspect whether false triggers are one-frame spikes or sustained high scores.

## Training remediation after chain verification

Only after identifying genuine model errors:

- mix audited open-domain natural speech/background during real-data fine-tuning to prevent forgetting;
- hard-mine stable failures by parent family rather than duplicating clips;
- add measured device EQ/RIR/noise/AGC/gain conditions to both positive and negative data;
- retain an untouched external dev/test set for checkpoint and final evaluation;
- optimize the declared FRR/open-domain FA/h operating point, with hard negatives reported separately.
