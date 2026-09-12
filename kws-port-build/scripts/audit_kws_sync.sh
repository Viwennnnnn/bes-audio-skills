#!/usr/bin/env bash
set -euo pipefail

sdk_root="${1:?usage: audit_kws_sync.sh /path/to/bes1700_main_v2}"
source_dir="$sdk_root/metabounds/configs/g19_pav/multimedia/smf/vad_v3"
target_dir="$sdk_root/metabounds/configs/g28_rm1/multimedia/smf/vad_v3"
files=(
  "vad_algo.cpp"
  "mj_kws.h"
  "inlcude/mj_kws.h"
  "lib/M33_lib/libmjkwsfix.a"
)

status=0
for relative_path in "${files[@]}"; do
  source_file="$source_dir/$relative_path"
  target_file="$target_dir/$relative_path"
  if [[ ! -f "$source_file" || ! -f "$target_file" ]]; then
    printf 'MISSING  %s\n' "$relative_path"
    status=1
    continue
  fi
  source_hash="$(sha256sum "$source_file" | awk '{print $1}')"
  target_hash="$(sha256sum "$target_file" | awk '{print $1}')"
  if [[ "$source_hash" == "$target_hash" ]]; then
    printf 'MATCH    %s  %s\n' "$relative_path" "$source_hash"
  else
    printf 'DIFFER   %s\n  G19 %s\n  G28 %s\n' "$relative_path" "$source_hash" "$target_hash"
    status=1
  fi
done

exit "$status"
