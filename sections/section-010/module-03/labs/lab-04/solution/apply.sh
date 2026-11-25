#!/usr/bin/env bash
set -euo pipefail
context="${ASTRONA_KUBE_CONTEXT:-kind-astro-ats-031-lab-010-03-04}"
if [[ "$(kubectl config current-context)" != "$context" ]]; then
  printf 'Refusing to operate on another Kubernetes context\n' >&2
  exit 1
fi
solution_directory="$(cd "$(dirname "$0")" && pwd)"
rogue_ip="$(kubectl -n outpost-031-010-03-04 get pod rogue -o jsonpath='{.status.podIP}')"
sed "s|<ROGUE_IP>|$rogue_ip|" "$solution_directory/networkpolicy-ledger-from-pod-range.yaml" | kubectl apply -f -
