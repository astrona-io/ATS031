#!/usr/bin/env bash
# Reference solution: verify the manifest signature, find the cache with the
# genuine fleet-agent, install it as root with mode 0755, lock down the
# install directories, verify the installed copy and record the result.
set -euo pipefail
context="${ASTRONA_KUBE_CONTEXT:-kind-astro-ats-031-lab-050-01-03}"
if [[ "$(kubectl config current-context)" != "$context" ]]; then
  printf 'Refusing to operate on another Kubernetes context\n' >&2
  exit 1
fi
cluster="${ASTRONA_KIND_CLUSTER:-astro-ats-031-lab-050-01-03}"
engine="${ASTRONA_CONTAINER_ENGINE:-podman}"
node_name="$cluster-control-plane"
release=/var/lib/fleet-release
"$engine" exec "$node_name" openssl dgst -sha256 -verify "$release/publisher.pub" \
  -signature "$release/SHA256SUMS.sig" "$release/SHA256SUMS"
trusted_digest=$("$engine" exec "$node_name" cut -d' ' -f1 "$release/SHA256SUMS")
for cache in cache-1 cache-2 cache-3; do
  digest=$("$engine" exec "$node_name" sha256sum "/var/cache/fleet/$cache/fleet-agent" | cut -d' ' -f1)
  if [[ "$digest" == "$trusted_digest" ]]; then
    genuine_cache="$cache"
  fi
done
"$engine" exec "$node_name" chown root:root /opt/fleet /opt/fleet/bin
"$engine" exec "$node_name" chmod 0755 /opt/fleet /opt/fleet/bin
"$engine" exec "$node_name" install -o root -g root -m 0755 "/var/cache/fleet/$genuine_cache/fleet-agent" /opt/fleet/bin/fleet-agent
"$engine" exec -w /opt/fleet/bin "$node_name" sha256sum --check "$release/SHA256SUMS"
kubectl -n starfleet-031-050-01-03 create configmap install-record \
  --from-literal=cache="$genuine_cache" --from-literal=sha256="$trusted_digest" \
  --dry-run=client -o yaml | kubectl apply -f -
