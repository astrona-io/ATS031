#!/usr/bin/env bash
# Reference solution: verify the signature of each mirror's manifest with the
# publisher key, check the binary against the authenticated manifest, and
# record the one mirror that passes both checks.
set -euo pipefail
context="${ASTRONA_KUBE_CONTEXT:-kind-astro-ats-031-lab-050-01-02}"
if [[ "$(kubectl config current-context)" != "$context" ]]; then
  printf 'Refusing to operate on another Kubernetes context\n' >&2
  exit 1
fi
cluster="${ASTRONA_KIND_CLUSTER:-astro-ats-031-lab-050-01-02}"
engine="${ASTRONA_CONTAINER_ENGINE:-podman}"
node_name="$cluster-control-plane"
release=/var/lib/relay-release
for mirror in a b c; do
  folder="$release/mirror-$mirror"
  if "$engine" exec "$node_name" openssl dgst -sha256 -verify "$release/publisher.pub" \
      -signature "$folder/SHA256SUMS.sig" "$folder/SHA256SUMS" >/dev/null 2>&1 \
    && "$engine" exec -w "$folder" "$node_name" sha256sum --check --status --strict SHA256SUMS; then
    trusted_digest=$("$engine" exec "$node_name" cut -d' ' -f1 "$folder/SHA256SUMS")
    kubectl -n starfleet-031-050-01-02 create configmap artifact-review \
      --from-literal=mirror="$mirror" --from-literal=sha256="$trusted_digest" \
      --dry-run=client -o yaml | kubectl apply -f -
    exit 0
  fi
done
echo 'No mirror passed both checks' >&2
exit 1
