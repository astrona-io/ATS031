#!/usr/bin/env bash
set -euo pipefail
context="${ASTRONA_KUBE_CONTEXT:-kind-astro-ats-031-lab-010-02-01}"
if [[ "$(kubectl config current-context)" != "$context" ]]; then
  printf 'Refusing to operate on another Kubernetes context\n' >&2
  exit 1
fi
solution_directory="$(cd "$(dirname "$0")" && pwd)"
kubectl apply -f "$solution_directory/networkpolicy-default-deny-all.yaml"
kubectl apply -f "$solution_directory/networkpolicy-forge-from-smith.yaml"
kubectl apply -f "$solution_directory/networkpolicy-smith-to-forge.yaml"
