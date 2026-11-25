#!/usr/bin/env bash
# Runs in a throwaway buildpack-deps container, which has gpg and dpkg-deb.
# Builds four small packages, a flat apt repository index (Packages and
# Release) and a detached signature of Release, then writes a tar archive of
# the repository to standard output. The private archive key stays in the
# container and is thrown away with it.
set -euo pipefail
export GNUPGHOME="$(mktemp -d)"
work="$(mktemp -d)"
repository="$work/fleet-apt"
mkdir -p "$repository/pool"
gpg --batch --quiet --passphrase '' --quick-gen-key 'Fleet Archive <archive@fleet.example>' rsa3072 sign never 2>/dev/null
gpg --batch --export 'archive@fleet.example' > "$repository/fleet-archive.gpg"
build_package() {
  local name="$1" version="$2" root
  shift 2
  root="$work/build/$name"
  mkdir -p "$root/DEBIAN"
  for file in "$@"; do
    mkdir -p "$root/$(dirname "$file")"
    printf '#!/bin/sh\n# %s from %s %s\necho %s\n' "$(basename "$file")" "$name" "$version" "$(od -An -N6 -tx1 /dev/urandom | tr -d ' \n')" > "$root/$file"
    chmod 0755 "$root/$file"
  done
  (cd "$root" && find . -type f ! -path './DEBIAN/*' -printf '%P\n' | sort | xargs md5sum > DEBIAN/md5sums)
  printf 'Package: %s\nVersion: %s\nArchitecture: all\nMaintainer: Fleet Archive <archive@fleet.example>\nSection: admin\nPriority: optional\nDescription: %s tools for the fleet nodes\n' \
    "$name" "$version" "$name" > "$root/DEBIAN/control"
  dpkg-deb --root-owner-group --build "$root" "$repository/pool/${name}_${version}_all.deb" >/dev/null
}
build_package fleet-tools 1.4.2 usr/lib/fleet-tools/check-node usr/lib/fleet-tools/rotate-logs usr/lib/fleet-tools/sync-clock usr/lib/fleet-tools/report-health
build_package fleet-agent 2.0.1 usr/lib/fleet-agent/agent usr/lib/fleet-agent/agent-ctl
build_package fleet-probe 0.9.7 usr/lib/fleet-probe/probe usr/lib/fleet-probe/probe-report
build_package fleet-docs 1.0.0 usr/lib/fleet-docs/show-docs
cd "$repository"
for deb in pool/*.deb; do
  dpkg-deb --field "$deb"
  printf 'Filename: %s\nSize: %s\nSHA256: %s\n\n' "$deb" "$(stat -c %s "$deb")" "$(sha256sum "$deb" | cut -d' ' -f1)"
done > Packages
{
  printf 'Origin: Fleet\nLabel: Fleet\nSuite: stable\nCodename: fleet\nDate: %s\nArchitectures: all\nComponents: main\nSHA256:\n' "$(date -u -R)"
  printf ' %s %s Packages\n' "$(sha256sum Packages | cut -d' ' -f1)" "$(stat -c %s Packages)"
} > Release
gpg --batch --quiet --local-user 'archive@fleet.example' --armor --detach-sign --output Release.gpg Release
tar -C "$work" -cf - fleet-apt
