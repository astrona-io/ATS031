#!/usr/bin/env bash
# Runs inside the control plane node container. Stages seven control plane
# binaries (random stand-ins) with digest-only .sha256 files. One binary,
# chosen at random, gets one changed byte in place: its size and its
# modification time stay the same, so only a digest shows the change.
set -euo pipefail
bundle=/var/lib/node-bundle
flip_byte() {
  local file="$1" size offset original
  size=$(stat -c %s "$file")
  offset=$(( (RANDOM * 32768 + RANDOM) % size ))
  original=$(od -An -tu1 -j "$offset" -N1 "$file" | tr -d ' ')
  printf "$(printf '\\%03o' $(( original ^ 255 )))" | dd of="$file" bs=1 seek="$offset" count=1 conv=notrunc status=none
}
binaries=(kube-apiserver kube-controller-manager kube-scheduler kube-proxy kubectl kubeadm kubelet)
rm -rf "$bundle"
mkdir -p "$bundle"
cd "$bundle"
for binary in "${binaries[@]}"; do
  head -c 32768 /dev/urandom > "$binary"
  sha256sum "$binary" | cut -d' ' -f1 | tr -d '\n' > "$binary.sha256"
  chmod 0755 "$binary"
done
changed=$(printf '%s\n' "${binaries[@]}" | shuf -n 1)
flip_byte "$changed"
touch -r kubectl.sha256 "${binaries[@]}"
echo "Staged $bundle"
