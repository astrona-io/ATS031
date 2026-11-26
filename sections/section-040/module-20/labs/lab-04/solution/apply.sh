#!/usr/bin/env bash
set -euo pipefail
context="${ASTRONA_KUBE_CONTEXT:-kind-astro-ats-031-lab-040-02-04}"
if [[ "$(kubectl config current-context)" != "$context" ]]; then
  printf 'Refusing to operate on another Kubernetes context\n' >&2
  exit 1
fi
solution_directory="$(cd "$(dirname "$0")" && pwd)"
# outpost: widen the selector to every pod. dock: add the missing policy.
kubectl apply -f "$solution_directory/networkpolicy-block-metadata-outpost.yaml"
kubectl apply -f "$solution_directory/networkpolicy-block-metadata-dock.yaml"
# starfleet: keep the block and add the exception for the labelled agent.
kubectl apply -f "$solution_directory/networkpolicy-allow-metadata-agent.yaml"
