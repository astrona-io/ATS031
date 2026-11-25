#!/usr/bin/env bash
set -euo pipefail
context="${ASTRONA_KUBE_CONTEXT:-kind-astro-ats-031-lab-040-01-01}"
if [[ "$(kubectl config current-context)" != "$context" ]]; then
  printf 'Refusing to operate on another Kubernetes context\n' >&2
  exit 1
fi
kubectl -n starfleet-031-040-01-01 patch deployment relay --type json \
  -p '[{"op": "remove", "path": "/spec/template/spec/hostNetwork"}]'
kubectl -n starfleet-031-040-01-01 rollout status deployment/relay --timeout=180s
