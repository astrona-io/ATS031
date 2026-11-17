#!/usr/bin/env bash
set -euo pipefail
context="${ASTRONA_KUBE_CONTEXT:-kind-astro-ats-031-lab-010-03-02}"
if [[ "$(kubectl config current-context)" != "$context" ]]; then
  printf 'Refusing to operate on another Kubernetes context\n' >&2
  exit 1
fi
lab_directory="$(cd "$(dirname "$0")/.." && pwd)"
kubectl apply -f "$lab_directory/bootstrap/manifests/start.yaml"
kubectl -n dock-031-010-03-02 wait --for=condition=Ready pod/assay --timeout=180s
kubectl -n dock-031-010-03-02 wait --for=condition=Ready pod/sampler --timeout=180s
kubectl -n starfleet-031-010-03-02 wait --for=condition=Ready pod/sampler --timeout=180s
kubectl -n starfleet-031-010-03-02 wait --for=condition=Ready pod/idler --timeout=180s
kubectl -n outpost-031-010-03-02 wait --for=condition=Ready pod/sampler --timeout=180s
