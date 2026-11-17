#!/usr/bin/env bash
# Runs inside the control plane node container. Stages six release files and a
# SHA256SUMS manifest, then changes one byte in one to three random files. The
# file sizes and modification times stay the same, so only a digest check
# shows which files changed.
set -euo pipefail
release=/var/lib/fleet-release
flip_byte() {
  local file="$1" size offset original
  size=$(stat -c %s "$file")
  offset=$(( (RANDOM * 32768 + RANDOM) % size ))
  original=$(od -An -tu1 -j "$offset" -N1 "$file" | tr -d ' ')
  printf "$(printf '\\%03o' $(( original ^ 255 )))" | dd of="$file" bs=1 seek="$offset" count=1 conv=notrunc status=none
}
rm -rf "$release"
mkdir -p "$release"
cd "$release"
files=(fleet-agent fleet-cli fleet-proxy fleet-sync fleet-scan fleet-init)
for name in "${files[@]}"; do
  head -c $(( 65536 + RANDOM % 8192 )) /dev/urandom > "$name"
  chmod 0755 "$name"
done
sha256sum "${files[@]}" > SHA256SUMS
for name in $(printf '%s\n' "${files[@]}" | shuf -n $(( 1 + RANDOM % 3 ))); do
  flip_byte "$name"
done
touch -r SHA256SUMS "${files[@]}"
echo "Staged $release"
