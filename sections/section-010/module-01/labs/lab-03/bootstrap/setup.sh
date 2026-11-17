#!/usr/bin/env bash
set -euo pipefail
context="${ASTRONA_KUBE_CONTEXT:-kind-astro-ats-031-lab-010-01-03}"
if [[ "$(kubectl config current-context)" != "$context" ]]; then
  printf 'Refusing to operate on another Kubernetes context\n' >&2
  exit 1
fi
lab_directory="$(cd "$(dirname "$0")/.." && pwd)"
kubectl apply -f "$lab_directory/bootstrap/manifests/start.yaml"
kubectl -n starfleet-031-010-01-03 wait --for=condition=Ready pod/relay --timeout=180s
kubectl -n starfleet-031-010-01-03 wait --for=condition=Ready pod/lander --timeout=180s
kubectl -n starfleet-031-010-01-03 wait --for=condition=Ready pod/courier --timeout=180s
