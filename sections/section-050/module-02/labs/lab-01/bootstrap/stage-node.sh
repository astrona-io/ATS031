#!/usr/bin/env bash
# Runs inside the control plane node container. Stages an offline mirror with
# the layout of the Kubernetes release site: release/<version>/bin/linux/<arch>/
# with three binaries and their .sha256 files. The binaries are small random
# stand-ins; only their digests matter. The stable version is chosen at random.
set -euo pipefail
mirror=/var/lib/k8s-mirror
rm -rf "$mirror"
versions=(v1.33.7 v1.34.3 v1.35.1 v1.36.0-alpha.2)
for version in "${versions[@]}"; do
  for arch in amd64 arm64; do
    folder="$mirror/release/$version/bin/linux/$arch"
    mkdir -p "$folder"
    for tool in kubectl kubeadm kubelet; do
      head -c $(( 4096 + RANDOM % 4096 )) /dev/urandom > "$folder/$tool"
      sha256sum "$folder/$tool" | cut -d' ' -f1 | tr -d '\n' > "$folder/$tool.sha256"
    done
  done
done
stable=$(printf '%s\n' v1.33.7 v1.34.3 v1.35.1 | shuf -n 1)
printf '%s' "$stable" > "$mirror/release/stable.txt"
printf '%s' v1.33.7 > "$mirror/release/stable-1.33.txt"
printf '%s' v1.34.3 > "$mirror/release/stable-1.34.txt"
printf '%s' v1.35.1 > "$mirror/release/stable-1.35.txt"
printf '%s' v1.36.0-alpha.2 > "$mirror/release/latest.txt"
echo "Staged $mirror"
