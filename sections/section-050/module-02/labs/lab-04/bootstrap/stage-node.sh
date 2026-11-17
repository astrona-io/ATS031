#!/usr/bin/env bash
# Runs inside the control plane node container. Stages a published digest
# index for kubectl (two versions, two architectures) and five download
# batches. Each batch has one cause, drawn at random without repeats:
#   ok              the file and the shipped checksum match the published digest
#   stale-checksum  the file matches the published digest, the shipped checksum is old
#   wrong-arch      the file is the published kubectl for the other architecture
#   wrong-version   the file is the published kubectl of v1.34.4 for this architecture
#   tampered        the file matches no published digest; the shipped checksum was
#                   rewritten to match it
# The binaries are random stand-ins; only their digests matter.
set -euo pipefail
index=/var/lib/release-index
incoming=/var/lib/k8s-incoming
rm -rf "$index" "$incoming"
case "$(uname -m)" in
  x86_64) node_arch=amd64; other_arch=arm64 ;;
  aarch64) node_arch=arm64; other_arch=amd64 ;;
esac
work=$(mktemp -d)
trap 'rm -rf "$work"' EXIT
for version in v1.34.4 v1.35.0; do
  for arch in amd64 arm64; do
    head -c $(( 24576 + RANDOM % 8192 )) /dev/urandom > "$work/kubectl-$version-$arch"
    mkdir -p "$index/release/$version/bin/linux/$arch"
    sha256sum "$work/kubectl-$version-$arch" | cut -d' ' -f1 | tr -d '\n' > "$index/release/$version/bin/linux/$arch/kubectl.sha256"
  done
done
digest_only() { sha256sum "$1" | cut -d' ' -f1 | tr -d '\n'; }
causes=($(printf '%s\n' ok stale-checksum wrong-arch wrong-version tampered | shuf))
for number in 1 2 3 4 5; do
  batch="$incoming/batch-$number"
  mkdir -p "$batch"
  printf 'release/v1.35.0/bin/linux/%s/kubectl\n' "$node_arch" > "$batch/SOURCE"
  case "${causes[$(( number - 1 ))]}" in
    ok) cp "$work/kubectl-v1.35.0-$node_arch" "$batch/kubectl" ;;
    stale-checksum) cp "$work/kubectl-v1.35.0-$node_arch" "$batch/kubectl" ;;
    wrong-arch) cp "$work/kubectl-v1.35.0-$other_arch" "$batch/kubectl" ;;
    wrong-version) cp "$work/kubectl-v1.34.4-$node_arch" "$batch/kubectl" ;;
    tampered) head -c "$(stat -c %s "$work/kubectl-v1.35.0-$node_arch")" /dev/urandom > "$batch/kubectl" ;;
  esac
  if [[ "${causes[$(( number - 1 ))]}" == stale-checksum ]]; then
    head -c 64 /dev/urandom | sha256sum | cut -d' ' -f1 | tr -d '\n' > "$batch/kubectl.sha256"
  else
    digest_only "$batch/kubectl" > "$batch/kubectl.sha256"
  fi
  chmod 0644 "$batch/kubectl"
done
echo "Staged $index and $incoming"
