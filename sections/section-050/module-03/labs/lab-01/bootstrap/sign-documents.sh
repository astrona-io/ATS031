#!/usr/bin/env bash
# Runs in a throwaway buildpack-deps container, which has gpg. Creates a
# publisher key and an unrelated key, signs six documents, damages a random
# subset of two or three, and writes a tar archive of the result to standard
# output. Only the publisher's public key leaves the container; both private
# keys are thrown away with the container.
set -euo pipefail
export GNUPGHOME="$(mktemp -d)"
work="$(mktemp -d)"
output="$work/doc-review"
mkdir -p "$output"
gpg --batch --quiet --passphrase '' --quick-gen-key 'Fleet Publisher <publisher@fleet.example>' rsa3072 sign never 2>/dev/null
gpg --batch --quiet --passphrase '' --quick-gen-key 'Fleet Mirror <mirror@fleet.example>' rsa3072 sign never 2>/dev/null
gpg --batch --export 'publisher@fleet.example' > "$output/publisher.gpg"
documents=(flight-plan.txt crew-roster.txt fuel-report.txt nav-update.txt comms-schedule.txt cargo-manifest.txt)
for document in "${documents[@]}"; do
  printf '%s\nissued: %s\nserial: %s\n' "$document" "$(date -u +%Y-%m-%d)" "$(od -An -N8 -tx1 /dev/urandom | tr -d ' \n')" > "$output/$document"
done
bad_count=$(( 2 + RANDOM % 2 ))
mapfile -t bad_documents < <(printf '%s\n' "${documents[@]}" | shuf -n "$bad_count")
mapfile -t damages < <(printf '%s\n' changed other-key missing | shuf)
for document in "${documents[@]}"; do
  damage=none
  for index in "${!bad_documents[@]}"; do
    if [[ "${bad_documents[$index]}" == "$document" ]]; then damage="${damages[$index]}"; fi
  done
  case "$damage" in
    none) gpg --batch --quiet --local-user 'publisher@fleet.example' --armor --detach-sign --output "$output/$document.asc" "$output/$document" ;;
    changed)
      gpg --batch --quiet --local-user 'publisher@fleet.example' --armor --detach-sign --output "$output/$document.asc" "$output/$document"
      sed -i 's/^serial: \(.*\)$/serial: \1-2/' "$output/$document" ;;
    other-key) gpg --batch --quiet --local-user 'mirror@fleet.example' --armor --detach-sign --output "$output/$document.asc" "$output/$document" ;;
    missing) ;;
  esac
done
tar -C "$work" -cf - doc-review
