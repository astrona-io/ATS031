#!/usr/bin/env bash
# Reference solution: check the manifest, then record the failing files and the
# current digest of fleet-agent in the ConfigMap manifest-check.
set -euo pipefail
context="${ASTRONA_KUBE_CONTEXT:-kind-astro-ats-031-lab-050-01-01}"
if [[ "$(kubectl config current-context)" != "$context" ]]; then
  printf 'Refusing to operate on another Kubernetes context\n' >&2
  exit 1
fi
cluster="${ASTRONA_KIND_CLUSTER:-astro-ats-031-lab-050-01-01}"
engine="${ASTRONA_CONTAINER_ENGINE:-podman}"
node_name="$cluster-control-plane"
failed_files=$("$engine" exec -w /var/lib/fleet-release "$node_name" sha256sum --check --quiet SHA256SUMS 2>/dev/null | cut -d: -f1 | paste -sd, - || true)
agent_digest=$("$engine" exec "$node_name" sha256sum /var/lib/fleet-release/fleet-agent | cut -d' ' -f1)
kubectl -n starfleet-031-050-01-01 create configmap manifest-check \
  --from-literal=failed="$failed_files" --from-literal=agent-sha256="$agent_digest" \
  --dry-run=client -o yaml | kubectl apply -f -
