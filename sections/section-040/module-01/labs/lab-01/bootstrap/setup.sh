#!/usr/bin/env bash
set -euo pipefail
context="${ASTRONA_KUBE_CONTEXT:-kind-astro-ats-031-lab-040-01-01}"
if [[ "$(kubectl config current-context)" != "$context" ]]; then
  printf 'Refusing to operate on another Kubernetes context\n' >&2
  exit 1
fi
lab_directory="$(cd "$(dirname "$0")/.." && pwd)"
kubectl apply -f "$lab_directory/bootstrap/manifests/start.yaml"
kubectl -n starfleet-031-040-01-01 rollout status deployment/probe --timeout=180s
kubectl -n starfleet-031-040-01-01 rollout status deployment/relay --timeout=180s
kubectl -n starfleet-031-040-01-01 wait --for=condition=Ready pod/metadata-simulator --timeout=180s
kubectl -n outpost-031-040-01-01 wait --for=condition=Ready pod/drifter --timeout=180s
