# Export and firmware integration

## Reproducible export package

Keep one immutable directory per export version. Include, when applicable:

- deployment manifest and schema version;
- source checkpoint hash and model/config identifiers;
- frontend, graph, tensor-shape, state, and trigger contracts;
- quantization table and calibration manifest hash;
- generated parameter blob/C arrays and their hash/CRC;
- generated public header and ABI/version constants;
- host fixed-point reference or library;
- golden inputs and intermediate/output digests;
- build command/toolchain/container or environment summary;
- resource estimate and validation report.

Generated artifacts should carry a machine-readable model/export ID. Avoid timestamps as the only identity. Make the exporter deterministic or document unavoidable differences.

## Parameter layout

Before packing, verify tensor names, shapes, gate/order conventions, transposes, padding, per-channel scale axis, alignment, endianness, and byte count. Generate compile-time assertions for dimensions and offsets where possible. After packing, parse the exported blob independently and compare values/hashes with the canonical quantized tensors.

## C API and static library contract

Define lifecycle and ownership clearly: size query, caller/library allocation, alignment, initialization, process frame size, state cleanup/reset, result fields, error behavior, and thread/reentrancy assumptions. Keep declarations, implementations, and linked library from the same export. Detect ABI drift with header/library version symbols or an exported configuration query.

Build a host harness against the same public header and library before firmware integration. Test valid input, zero/silence, extrema, wrong sizes, reset/repeatability, chunk boundaries, and long streaming state.

## Firmware integration

Trace the real data path from PCM producer through buffering, frontend/model call, trigger event, and consumer. Confirm sample rate, channels, bit depth, interleaving, frame units (bytes versus samples), cache/chunk behavior, memory regions, alignment, logging, and reset conditions.

Verify the build system actually selects the new source/library for the target core. Inspect map files, symbols, strings, hashes, and timestamps. If another image embeds the algorithm core image, rebuild the complete dependency chain required for the flashing package.

## Delivery checks

Record:

- compiler/toolchain flags and target ISA/FPU/DSP options;
- library and final image hashes;
- Flash/code/rodata, persistent/peak RAM, scratch, stack, and heap ownership;
- cycles per frame, worst-case latency, scheduling jitter, and real-time headroom;
- exact flashing manifest/partition/address and rollback artifact.

A copied library is not deployed until the final flashed image is proven to contain it.
