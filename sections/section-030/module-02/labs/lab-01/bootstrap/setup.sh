#!/usr/bin/env bash
set -euo pipefail
context="${ASTRONA_KUBE_CONTEXT:-kind-astro-ats-031-lab-030-02-01}"
if [[ "$(kubectl config current-context)" != "$context" ]]; then
  printf 'Refusing to operate on another Kubernetes context\n' >&2
  exit 1
fi
lab_directory="$(cd "$(dirname "$0")/.." && pwd)"
kubectl apply -f "$lab_directory/bootstrap/manifests/start.yaml"
kubectl -n starfleet-031-030-02-01 rollout status deployment/probe --timeout=180s
kubectl -n starfleet-031-030-02-01 rollout status deployment/scout --timeout=180s
kubectl -n ingress-system rollout status deployment/traefik --timeout=180s
