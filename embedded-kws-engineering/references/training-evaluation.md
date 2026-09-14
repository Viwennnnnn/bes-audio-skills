# Streaming KWS training and evaluation

## Freeze the comparison protocol

Before training, pin:

- exact manifests and their hashes;
- model name, dimensions, parameter count, causal state/cache behavior;
- frontend sample rate, feature type, FFT/window/hop, mel bins, centering, normalization;
- optimizer, learning rate, weight decay, clipping, epochs, seed, batch/category sampler;
- online/offline augmentations and their probabilities;
- evaluation cadence, DET implementation, checkpoint rule, target operating point;
- output directory and whether initialization is random or from a named checkpoint.

For model comparisons, change the model only unless the experiment explicitly studies another factor. Store every model in an independent output directory.

## Categories and sampling

Keep at least these concepts distinct:

- positive target utterances;
- hard negatives or confusing phrases;
- open-domain natural speech;
- background/noise/music.

Balanced sampling means a deliberate per-batch or per-epoch quota, not necessarily the raw manifest distribution. Report both the raw distribution and the sampled distribution. Oversampling does not create new information; track unique families as well as sampled rows.

## Augmentation

Apply family isolation before any augmentation. Start with mild transformations whose deployment relevance is understood. Candidate stages include speed, gain, measured device EQ, room impulse responses, public noise at controlled SNR, microphone noise, AGC dynamics, and codec effects.

Use the same domain transformations on positive and negative speech unless there is a justified asymmetry. Keep a no-new-augmentation baseline. Add one augmentation family at a time so changes can be attributed.

For scarce real data, a sound pattern is synthetic/public pretraining followed by speaker/session-isolated real-domain fine-tuning. During fine-tuning, mix enough audited open-domain speech/background to avoid catastrophic loss of false-alarm robustness. Do not use held-out real speakers to derive augmentation statistics if strict isolation is claimed.

## Streaming windows

A window classifier is not inherently limited to one second. For slow keywords longer than the nominal window, use causal sliding windows or a streaming receptive field with overlap/state. Ensure training contains full slow utterances and label frames/windows consistently. Do not blindly truncate long positives. Verify latency, receptive field, and state reset behavior under continuous input.

## Checkpoint and threshold selection

Use dev only. A typical selection procedure is:

1. Produce frame-level scores for each evaluated checkpoint.
2. Sweep threshold and any fixed temporal trigger rule.
3. Within the allowed open-domain FA/h target, choose the operating point with minimum FRR.
4. Break ties using lower actual FA/h, then earlier epoch or another predeclared rule.
5. Keep hard-negative trigger rate as a separate constraint or tie-breaker.
6. Freeze checkpoint, threshold, smoothing, and trigger logic.
7. Evaluate frozen test once.

If no threshold satisfies the target, report that fact; do not quietly redefine the denominator or include/exclude categories after seeing results.

## Metrics

- `FRR = missed positive files / valid positive files` under the declared trigger window.
- Sample trigger rate is useful for localization but is not FA/h.
- `event FA/h = valid false-trigger events / actual evaluated open-domain hours`.
- Also report triggered-file FA/h when useful, clearly labeled.
- Do not include inter-file waits in audio-exposure FA/h unless the test is explicitly a wall-clock product trial.
- Do not count hard negatives in open-domain FA/h.
- Exclude abnormal attempts from algorithm denominators and report them separately.

CV accuracy is a coarse loss-loop diagnostic. It can look good while the operational threshold produces unacceptable FRR or FA/h.

## Speaker-paired cross-validation

For paired male/female folds, assign complete speakers to train/dev/test. Rotate test pairs and independent validation pairs so every speaker appears in each held-out role as intended. Assert no speaker/session/family overlap and verify every speaker appears exactly once in OOF test when that is the protocol.

Initialize every fold from the same untouched base checkpoint. Choose checkpoint/threshold within each fold's validation set, then score that fold's unseen test pair. Aggregate OOF decisions using each fold's frozen validation threshold. Report pooled totals and fold mean, standard deviation, best/worst fold, sex/speaker distributions, and sample count coverage.

## Deployment-oriented model comparison

Useful candidates may include compact GRU, causal depthwise-separable TCN, MDTC, FSMN, DS-CNN, TC-ResNet, or BC-ResNet variants. The final choice depends on measured FRR/FA tradeoff and implementation cost, not architecture reputation.

Measure parameters, persistent state, peak RAM, Flash, operations/frame, latency, quantization sensitivity, and float/fixed-point agreement. Causal claims require right context zero or an explicitly accepted latency. If effect matters more than keeping an existing C frontend, say so, but still budget the port and validate it.
