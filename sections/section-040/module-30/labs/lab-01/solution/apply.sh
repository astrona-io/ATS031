#!/usr/bin/env bash
set -euo pipefail
context="${ASTRONA_KUBE_CONTEXT:-kind-astro-ats-031-lab-040-03-01}"
if [[ "$(kubectl config current-context)" != "$context" ]]; then
  printf 'Refusing to operate on another Kubernetes context\n' >&2
  exit 1
fi
cluster="${ASTRONA_KIND_CLUSTER:-astro-ats-031-lab-040-03-01}"
engine="${ASTRONA_CONTAINER_ENGINE:-podman}"
worker_name="$cluster-worker"

# Close the read-only port in the kubelet configuration file, then restart the kubelet.
"$engine" exec "$worker_name" sed -i 's/^readOnlyPort:.*/readOnlyPort: 0/' /var/lib/kubelet/config.yaml
"$engine" exec "$worker_name" systemctl restart kubelet
sleep 10
kubectl wait --for=condition=Ready "node/$worker_name" --timeout=180s
