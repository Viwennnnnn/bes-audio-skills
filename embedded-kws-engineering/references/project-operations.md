# Project organization and run operations

## Workspace layout

Prefer a small stable core and versioned artifacts:

```text
project/
├── configs/
├── data_prep/<dataset_version>/
│   ├── registry/
│   ├── manifests/
│   ├── quarantine/
│   └── reports/
├── tools/
│   ├── data/
│   ├── train/
│   ├── eval/
│   └── deployment/
├── experiments/<experiment_name>/
│   ├── config.yaml
│   ├── run_command.txt
│   ├── preflight.json
│   ├── logs/
│   ├── checkpoints/
│   ├── scores/
│   └── reports/
└── archive/
```

Do not leave one-off scripts and scores in example roots. Promote reusable tools into a named tools area; keep experiment-specific helpers inside that experiment. Prefer references/registries over copying large audio trees.

## Cleanup

Inventory first with paths, sizes, timestamps, callers, and whether files are tracked. Distinguish active, reusable, historical reference, reproducible generated output, and disposable cache. Preserve user changes and anything whose provenance is uncertain.

When deletion is explicitly requested, resolve exact targets and report what was removed. Archive useful historical reports/configs before deleting obsolete non-baseline experiments. Never delete raw data or irreplaceable weights merely because disk is full.

If storage pressure appears unrelated to the scoped project, report filesystem usage and largest project-owned directories; do not modify other users' or system data. Escalate capacity issues to infrastructure owners when appropriate.

## Experiment preflight

Before launch, assert manifests/configs exist, categories are nonempty, forbidden evaluation data is absent, initialization is correct, outputs do not overwrite a baseline, and hashes are recorded. Run a short loader/forward/evaluation smoke test when practical.

Check GPUs immediately before launch. Prefer the lowest-utilization card with enough free memory and keep one heavy training/evaluation job per card unless the user explicitly accepts sharing. Record `CUDA_VISIBLE_DEVICES` and the physical/logical mapping.

## Monitoring

Read the actual process state, current log tail, checkpoint directory, and GPU state. Report meaningful changes: completed epoch, evaluation checkpoint ready, evaluation result, completion, OOM, data/decode error, or stalled process.

Do not equate a checkpoint file with successful evaluation. Training and evaluation status should be reported together when evaluation is part of the protocol. Do not stop, modify, or restart a monitored process unless authorized.

When convergence looks abnormal, compare against the reference run's exact initialization, sampler, frontend, learning rate, loss, batch count, augmentation, and metric definition. A low early accuracy can arise from a harder audited distribution or random initialization; use a controlled one-epoch initialization comparison to isolate causes.

## Reproducibility bundle

Keep configuration, exact command, environment summary, git/code revision, manifest/config/checkpoint hashes, logs, checkpoint selection record, scores/DET, and final reports together. Secrets and machine-specific credentials must stay outside the bundle.
