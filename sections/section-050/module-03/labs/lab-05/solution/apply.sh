#!/usr/bin/env bash
# Reference solution: apply the policy that requires @sha256: in every
# container and init container image, and bind it with Deny to the
# starfleet namespace only.
set -euo pipefail
context="${ASTRONA_KUBE_CONTEXT:-kind-astro-ats-031-lab-050-03-05}"
if [[ "$(kubectl config current-context)" != "$context" ]]; then
  printf 'Refusing to operate on another Kubernetes context\n' >&2
  exit 1
fi
solution_directory="$(cd "$(dirname "$0")" && pwd)"
kubectl apply -f "$solution_directory/validatingadmissionpolicy-require-image-digest.yaml"
kubectl apply -f "$solution_directory/validatingadmissionpolicybinding-require-image-digest.yaml"
