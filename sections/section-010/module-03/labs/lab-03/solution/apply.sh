#!/usr/bin/env bash
set -euo pipefail
context="${ASTRONA_KUBE_CONTEXT:-kind-astro-ats-031-lab-010-03-03}"
if [[ "$(kubectl config current-context)" != "$context" ]]; then
  printf 'Refusing to operate on another Kubernetes context\n' >&2
  exit 1
fi
solution_directory="$(cd "$(dirname "$0")" && pwd)"
kubectl label namespace survey-031-010-03-03 division=science --overwrite
kubectl label namespace salvage-031-010-03-03 division=science --overwrite
kubectl apply -f "$solution_directory/networkpolicy-archive-from-science.yaml"
