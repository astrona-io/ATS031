#!/usr/bin/env bash
set -euo pipefail
context="${ASTRONA_KUBE_CONTEXT:-kind-astro-ats-031-lab-020-02-01}"
if [[ "$(kubectl config current-context)" != "$context" ]]; then
  printf 'Refusing to operate on another Kubernetes context\n' >&2
  exit 1
fi
cluster="${ASTRONA_KIND_CLUSTER:-astro-ats-031-lab-020-02-01}"
engine="${ASTRONA_CONTAINER_ENGINE:-podman}"
lab_directory="$(cd "$(dirname "$0")/.." && pwd)"
node_name="$cluster-control-plane"
worker_name="$cluster-worker"
kubectl apply -f "$lab_directory/bootstrap/manifests/start.yaml"
kubectl -n starfleet-031-020-02-01 rollout status deployment/probe --timeout=180s
kubectl -n starfleet-031-020-02-01 wait --for=condition=Ready pod/shuttle --timeout=120s
kubectl -n outpost-031-020-02-01 wait --for=condition=Ready pod/drifter --timeout=120s
# The kube-bench image is preloaded on every node. Warn if it is missing.
for node in "$node_name" "$worker_name"; do
  "$engine" exec "$node" crictl images | grep -q 'aquasec/kube-bench' || printf 'Warning: kube-bench image not found on %s\n' "$node" >&2
done
