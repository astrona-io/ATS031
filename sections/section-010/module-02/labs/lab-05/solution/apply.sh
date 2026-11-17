#!/usr/bin/env bash
set -euo pipefail
context="${ASTRONA_KUBE_CONTEXT:-kind-astro-ats-031-lab-010-02-05}"
if [[ "$(kubectl config current-context)" != "$context" ]]; then
  printf 'Refusing to operate on another Kubernetes context\n' >&2
  exit 1
fi
solution_directory="$(cd "$(dirname "$0")" && pwd)"
kubectl label namespace cargo-031-010-02-05 netpol=restricted --overwrite
kubectl label namespace fuel-031-010-02-05 netpol=restricted --overwrite
for namespace in $(kubectl get namespaces -l netpol=restricted -o jsonpath='{.items[*].metadata.name}'); do
  kubectl -n "$namespace" apply -f "$solution_directory/networkpolicy-default-deny-all.yaml"
done
