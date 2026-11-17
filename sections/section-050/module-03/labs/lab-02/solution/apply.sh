#!/usr/bin/env bash
# Reference solution: verify the Release signature, check Packages against
# Release and every pool file against Packages, ask dpkg which installed
# fleet-tools file changed and record both findings.
set -euo pipefail
context="${ASTRONA_KUBE_CONTEXT:-kind-astro-ats-031-lab-050-03-02}"
if [[ "$(kubectl config current-context)" != "$context" ]]; then
  printf 'Refusing to operate on another Kubernetes context\n' >&2
  exit 1
fi
cluster="${ASTRONA_KIND_CLUSTER:-astro-ats-031-lab-050-03-02}"
engine="${ASTRONA_CONTAINER_ENGINE:-podman}"
node_name="$cluster-control-plane"
repository=/var/lib/fleet-apt
run_in_repository() { "$engine" exec -w "$repository" "$node_name" "$@"; }
run_in_repository gpgv --keyring ./fleet-archive.gpg Release.gpg Release
packages_digest=$(run_in_repository sed -n 's/^ \([0-9a-f]\{64\}\) [0-9]* Packages$/\1/p' Release)
printf '%s  Packages\n' "$packages_digest" | "$engine" exec -i -w "$repository" "$node_name" sha256sum --check
check_lines=$(run_in_repository awk '/^Filename:/ {file=$2} /^SHA256:/ {print $2 "  " file}' Packages)
bad_package=$(printf '%s\n' "$check_lines" | "$engine" exec -i -w "$repository" "$node_name" sha256sum --check 2>/dev/null | sed -n 's/: FAILED$//p' || true)
changed_file=$("$engine" exec "$node_name" dpkg --verify fleet-tools | awk 'substr($0, 3, 1) == "5" {print $NF}')
kubectl -n starfleet-031-050-03-02 create configmap repository-review \
  --from-literal=bad-package="$(basename "$bad_package")" --from-literal=changed-file="$changed_file" \
  --dry-run=client -o yaml | kubectl apply -f -
