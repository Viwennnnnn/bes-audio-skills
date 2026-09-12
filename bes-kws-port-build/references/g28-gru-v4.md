# Known G28 GRU v4 migration snapshot

Snapshot established on 2026-09-11. Revalidate it against the current checkout before acting.

## Before synchronization

G28 used `hello_agent_frontend_v4`:

- architecture: GRU_v4
- threshold: 0.94
- KWS AGC: disabled
- library SHA256: `185e515a8bc02c8d32745d8cbb67721b40ee2e41cab601e40233bf2c670b6090`

G19 PAV used:

- model: `v4_real_finetune_r1_gru_14`
- architecture: GRU_v4, not DS-TCN
- checkpoint: `v4_real_finetune_r1/gru/checkpoints/14.pt`
- threshold: 0.72
- KWS-only AGC: enabled
- library SHA256: `56cbebef99115c4650131dcd3d5eb02203ffbe9b26fe832097bfa54afb103484`
- metadata: `/home/huangweiwen/work/kws_deployment/m33_gru/models/v4_real_finetune_r1_gru_14/model.json`

## Synchronized G28 files

Relative to `metabounds/configs/g28_rm1/multimedia/smf/vad_v3/`:

- `lib/M33_lib/libmjkwsfix.a`
- `vad_algo.cpp`
- `mj_kws.h`
- `inlcude/mj_kws.h` (the directory spelling is present in the SDK)

The runtime also includes KWS-only AGC, periodic score/PCM peak/timing logs, state cleanup, and the `mj_kws_get_frontend_config` ABI declaration.

## Build and outputs

Known commands from the SDK root:

```bash
./build-meta.sh bth -b g28_rm1
./build-meta.sh -b g28_rm1 -d
```

The second is the full clean G28 build used for delivery. The examined successful build produced boot, OTA, m33c0, m55c1, and m55c0/AP images. The flashing directory is `out/`, with `out/firmware.json` as the manifest.

Important outputs include `out/nuttx_ap.bin`, `out/nuttx_apc1.bin`, `out/nuttx_bl.bin`, `out/nuttx_ota.bin`, `out/best1700_watch.bin`, `out/smf.json`, and `out/lv_assets_images.bin`. Check the current manifest rather than assuming every historical output is flashed.
