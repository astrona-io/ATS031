#!/usr/bin/env bash
set -euo pipefail
context="${ASTRONA_KUBE_CONTEXT:-kind-astro-ats-031-lab-040-02-03}"
if [[ "$(kubectl config current-context)" != "$context" ]]; then
  printf 'Refusing to operate on another Kubernetes context\n' >&2
  exit 1
fi
# The same corrected policy for all three namespaces: select every pod, allow
# all egress except the metadata address.
solution_directory="$(cd "$(dirname "$0")" && pwd)"
kubectl replace -f "$solution_directory/networkpolicy-metadata-guard-starfleet.yaml"
kubectl replace -f "$solution_directory/networkpolicy-metadata-guard-outpost.yaml"
kubectl replace -f "$solution_directory/networkpolicy-metadata-guard-dock.yaml"
