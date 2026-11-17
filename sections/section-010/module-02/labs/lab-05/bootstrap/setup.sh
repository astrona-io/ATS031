#!/usr/bin/env bash
set -euo pipefail
context="${ASTRONA_KUBE_CONTEXT:-kind-astro-ats-031-lab-010-02-05}"
if [[ "$(kubectl config current-context)" != "$context" ]]; then
  printf 'Refusing to operate on another Kubernetes context\n' >&2
  exit 1
fi
lab_directory="$(cd "$(dirname "$0")/.." && pwd)"
kubectl apply -f "$lab_directory/bootstrap/manifests/start.yaml"
kubectl -n cargo-031-010-02-05 wait --for=condition=Ready pod/loader --timeout=180s
kubectl -n fuel-031-010-02-05 wait --for=condition=Ready pod/pump --timeout=180s
kubectl -n galley-031-010-02-05 wait --for=condition=Ready pod/cook --timeout=180s
