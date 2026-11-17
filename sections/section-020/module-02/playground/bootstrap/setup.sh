#!/usr/bin/env bash
set -euo pipefail
engine="${ASTRONA_CONTAINER_ENGINE:-podman}"
if [[ "$(kubectl config current-context)" != "kind-astro-ats-031-playground-020-02" ]]; then
  printf 'Refusing to operate on another Kubernetes context\n' >&2
  exit 1
fi
lab_directory="$(cd "$(dirname "$0")/.." && pwd)"
node_name="astro-ats-031-playground-020-02-control-plane"
worker_name="astro-ats-031-playground-020-02-worker"
kubectl apply -f "$lab_directory/bootstrap/manifests/start.yaml"
kubectl -n starfleet rollout status deployment/probe --timeout=180s
kubectl -n starfleet wait --for=condition=Ready pod/shuttle --timeout=120s
kubectl -n outpost wait --for=condition=Ready pod/drifter --timeout=120s
# The kube-bench image is preloaded on every node. Warn if it is missing.
for node in "$node_name" "$worker_name"; do
  "$engine" exec "$node" crictl images | grep -q 'aquasec/kube-bench' || printf 'Warning: kube-bench image not found on %s\n' "$node" >&2
done
