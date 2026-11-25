#!/usr/bin/env bash
# Runs inside the control plane node container. Stages three mirrors of the
# relay-agent release. Each mirror has the binary, a SHA256SUMS manifest and a
# signature over the manifest. The three roles are shuffled on every start:
#   genuine: publisher signature, binary matches the manifest
#   forged:  signature from another key, binary matches its own manifest
#   altered: publisher signature, one byte of the binary changed
# Both private keys are deleted after signing.
set -euo pipefail
release=/var/lib/relay-release
flip_byte() {
  local file="$1" size offset original
  size=$(stat -c %s "$file")
  offset=$(( (RANDOM * 32768 + RANDOM) % size ))
  original=$(od -An -tu1 -j "$offset" -N1 "$file" | tr -d ' ')
  printf "$(printf '\\%03o' $(( original ^ 255 )))" | dd of="$file" bs=1 seek="$offset" count=1 conv=notrunc status=none
}
rm -rf "$release"
mkdir -p "$release"
keys=$(mktemp -d)
trap 'rm -rf "$keys"' EXIT
openssl genpkey -algorithm RSA -pkeyopt rsa_keygen_bits:2048 -out "$keys/publisher.key" 2>/dev/null
openssl genpkey -algorithm RSA -pkeyopt rsa_keygen_bits:2048 -out "$keys/other.key" 2>/dev/null
openssl pkey -in "$keys/publisher.key" -pubout -out "$release/publisher.pub"
head -c $(( 98304 + RANDOM % 8192 )) /dev/urandom > "$keys/relay-agent"
roles=($(printf '%s\n' genuine forged altered | shuf))
mirrors=(a b c)
for index in 0 1 2; do
  mirror="$release/mirror-${mirrors[$index]}"
  mkdir -p "$mirror"
  case "${roles[$index]}" in
    genuine)
      cp "$keys/relay-agent" "$mirror/relay-agent"
      (cd "$mirror" && sha256sum relay-agent > SHA256SUMS)
      signing_key="$keys/publisher.key" ;;
    forged)
      head -c "$(stat -c %s "$keys/relay-agent")" /dev/urandom > "$mirror/relay-agent"
      (cd "$mirror" && sha256sum relay-agent > SHA256SUMS)
      signing_key="$keys/other.key" ;;
    altered)
      cp "$keys/relay-agent" "$mirror/relay-agent"
      (cd "$mirror" && sha256sum relay-agent > SHA256SUMS)
      flip_byte "$mirror/relay-agent"
      signing_key="$keys/publisher.key" ;;
  esac
  openssl dgst -sha256 -sign "$signing_key" -out "$mirror/SHA256SUMS.sig" "$mirror/SHA256SUMS"
  chmod 0755 "$mirror/relay-agent"
done
touch -r "$release/publisher.pub" "$release"/mirror-*/*
echo "Staged $release"
