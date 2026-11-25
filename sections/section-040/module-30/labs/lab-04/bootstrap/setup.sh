#!/usr/bin/env bash
set -euo pipefail
context="${ASTRONA_KUBE_CONTEXT:-kind-astro-ats-031-lab-040-03-04}"
if [[ "$(kubectl config current-context)" != "$context" ]]; then
  printf 'Refusing to operate on another Kubernetes context\n' >&2
  exit 1
fi
lab_directory="$(cd "$(dirname "$0")/.." && pwd)"

kubectl apply -f "$lab_directory/bootstrap/manifests/start.yaml"
kubectl -n dock-031-040-03-04 wait --for=condition=Ready pod/net-tool pod/port-watch pod/tender --timeout=180s
kubectl -n outpost-031-040-03-04 wait --for=condition=Ready pod/sniffer pod/debug-shell pod/drifter --timeout=180s
