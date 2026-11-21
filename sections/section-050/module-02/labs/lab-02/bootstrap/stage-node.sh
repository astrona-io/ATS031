#!/usr/bin/env bash
# Runs inside the control plane node container. Stages three downloads with
# the digest-only .sha256 files the release site publishes. In three starts
# out of four one download, chosen at random, has one changed byte; in the
# fourth start every download is intact.
set -euo pipefail
downloads=/var/lib/k8s-downloads
flip_byte() {
  local file="$1" size offset original
  size=$(stat -c %s "$file")
  offset=$(( (RANDOM * 32768 + RANDOM) % size ))
  original=$(od -An -tu1 -j "$offset" -N1 "$file" | tr -d ' ')
  printf "$(printf '\\%03o' $(( original ^ 255 )))" | dd of="$file" bs=1 seek="$offset" count=1 conv=notrunc status=none
}
rm -rf "$downloads"
mkdir -p "$downloads"
cd "$downloads"
for tool in kubectl kubeadm kubelet; do
  head -c $(( 16384 + RANDOM % 8192 )) /dev/urandom > "$tool"
  sha256sum "$tool" | cut -d' ' -f1 | tr -d '\n' > "$tool.sha256"
  chmod 0644 "$tool"
done
if (( RANDOM % 4 != 0 )); then
  flip_byte "$(printf '%s\n' kubectl kubeadm kubelet | shuf -n 1)"
fi
touch -r kubectl.sha256 kubectl kubeadm kubelet
# The grader compares the downloads with this list of staged digests.
mkdir -p /var/lib/astrona-lab
(cd "$downloads" && sha256sum kubectl kubeadm kubelet kubectl.sha256 kubeadm.sha256 kubelet.sha256) > /var/lib/astrona-lab/050-02-02-staged
chmod 0600 /var/lib/astrona-lab/050-02-02-staged
echo "Staged $downloads"
