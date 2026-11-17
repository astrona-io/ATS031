#!/usr/bin/env bash
# Runs inside the control plane node container, after setup.sh copied the
# cosign binary to /usr/local/bin. Creates a new fleet key pair, signs six
# build records with it, deletes the private key, and then damages two or
# three random records: changed content, a signature from another key, or a
# missing signature. Also prepares /var/lib/approval with approval.txt.
set -euo pipefail
records=/var/lib/build-records
approval=/var/lib/approval
keys="$(mktemp -d)"
rm -rf "$records" "$approval"
mkdir -p "$records" "$approval"
export COSIGN_PASSWORD=''
(cd "$keys" && cosign generate-key-pair --output-key-prefix fleet >/dev/null 2>&1)
(cd "$keys" && cosign generate-key-pair --output-key-prefix other >/dev/null 2>&1)
cp "$keys/fleet.pub" "$records/fleet.pub"
sign_record() {
  cosign sign-blob --yes --key "$keys/$1.key" --tlog-upload=false --output-signature "$records/$2.sig" "$records/$2" >/dev/null 2>&1
}
for component in agent probe relay scheduler gateway exporter; do
  record="build-$component.txt"
  printf 'component: fleet-%s\nversion: 1.%d.%d\ncommit: %s\nbuilder: fleet-ci\n' \
    "$component" $(( RANDOM % 9 )) $(( RANDOM % 20 )) "$(od -An -N20 -tx1 /dev/urandom | tr -d ' \n')" > "$records/$record"
  sign_record fleet "$record"
done
damage_count=$(( 2 + RANDOM % 2 ))
mapfile -t damaged < <(cd "$records" && ls build-*.txt | shuf -n "$damage_count")
mapfile -t damages < <(printf '%s\n' changed other-key missing | shuf -n "$damage_count")
for index in "${!damaged[@]}"; do
  record="${damaged[$index]}"
  case "${damages[$index]}" in
    changed) sed -i 's/^builder: fleet-ci$/builder: laptop-7/' "$records/$record" ;;
    other-key) sign_record other "$record" ;;
    missing) rm -f "$records/$record.sig" ;;
  esac
done
rm -rf "$keys"
printf 'release: fleet-%s\napproved-by: release-manager\n' "$(date -u +%Y%m%d)" > "$approval/approval.txt"
touch -r "$records/fleet.pub" "$records"/* "$approval/approval.txt"
echo "Staged $records and $approval"
