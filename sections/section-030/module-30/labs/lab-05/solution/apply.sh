#!/usr/bin/env bash
set -euo pipefail
context="${ASTRONA_KUBE_CONTEXT:-kind-astro-ats-031-lab-030-03-05}"
if [[ "$(kubectl config current-context)" != "$context" ]]; then
  printf 'Refusing to operate on another Kubernetes context\n' >&2
  exit 1
fi
lab_directory="$(cd "$(dirname "$0")/.." && pwd)"
solution_directory="$lab_directory/solution"
kubectl -n ingress-system create configmap traefik-dynamic --from-file="$solution_directory/dynamic.yaml" --dry-run=client -o yaml | kubectl apply -f -
kubectl apply -f "$solution_directory/ingress-harbor.yaml"
kubectl -n ingress-system patch deployment traefik --type=json --patch-file "$solution_directory/traefik-redirect-patch.json"
kubectl -n ingress-system rollout status deployment/traefik --timeout=180s
