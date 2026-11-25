#!/usr/bin/env bash
# Runs inside the control plane node container. Stages a signed manifest for
# fleet-agent, three download caches of which only one holds the genuine
# bytes (chosen at random), and an install directory that other users can
# write, with an old copy already in it.
set -euo pipefail
release=/var/lib/fleet-release
caches=/var/cache/fleet
flip_byte() {
  local file="$1" size offset original
  size=$(stat -c %s "$file")
  offset=$(( (RANDOM * 32768 + RANDOM) % size ))
  original=$(od -An -tu1 -j "$offset" -N1 "$file" | tr -d ' ')
  printf "$(printf '\\%03o' $(( original ^ 255 )))" | dd of="$file" bs=1 seek="$offset" count=1 conv=notrunc status=none
}
rm -rf "$release" "$caches" /opt/fleet
mkdir -p "$release"
keys=$(mktemp -d)
trap 'rm -rf "$keys"' EXIT
openssl genpkey -algorithm RSA -pkeyopt rsa_keygen_bits:2048 -out "$keys/publisher.key" 2>/dev/null
openssl pkey -in "$keys/publisher.key" -pubout -out "$release/publisher.pub"
head -c $(( 81920 + RANDOM % 8192 )) /dev/urandom > "$keys/fleet-agent"
(cd "$keys" && sha256sum fleet-agent > "$release/SHA256SUMS")
openssl dgst -sha256 -sign "$keys/publisher.key" -out "$release/SHA256SUMS.sig" "$release/SHA256SUMS"
roles=($(printf '%s\n' genuine flipped replaced | shuf))
for index in 0 1 2; do
  cache="$caches/cache-$(( index + 1 ))"
  mkdir -p "$cache"
  case "${roles[$index]}" in
    genuine) cp "$keys/fleet-agent" "$cache/fleet-agent" ;;
    flipped) cp "$keys/fleet-agent" "$cache/fleet-agent"; flip_byte "$cache/fleet-agent" ;;
    replaced) head -c "$(stat -c %s "$keys/fleet-agent")" /dev/urandom > "$cache/fleet-agent" ;;
  esac
  chmod 0755 "$cache/fleet-agent"
done
touch -r "$release/SHA256SUMS" "$caches"/cache-*/fleet-agent
# The install directory starts in an unsafe state: owned by user 1000 and
# writable by everyone, with an unverified copy installed.
mkdir -p /opt/fleet/bin
head -c 4096 /dev/urandom > /opt/fleet/bin/fleet-agent
chown -R 1000:1000 /opt/fleet
chmod 0775 /opt/fleet
chmod 0777 /opt/fleet/bin /opt/fleet/bin/fleet-agent
echo "Staged $release, $caches and /opt/fleet"
