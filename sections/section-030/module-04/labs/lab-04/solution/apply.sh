#!/usr/bin/env bash
set -euo pipefail
context="${ASTRONA_KUBE_CONTEXT:-kind-astro-ats-031-lab-030-04-04}"
if [[ "$(kubectl config current-context)" != "$context" ]]; then
  printf 'Refusing to operate on another Kubernetes context\n' >&2
  exit 1
fi
lab_directory="$(cd "$(dirname "$0")/.." && pwd)"
solution_directory="$lab_directory/solution"
kubectl apply -f "$solution_directory/role-traefik-secrets.yaml"
kubectl apply -f "$solution_directory/clusterrole-traefik.yaml"
kubectl -n ingress-system patch service traefik --type=json --patch-file "$solution_directory/traefik-service-patch.json"
kubectl -n ingress-system patch deployment traefik --type=json --patch-file "$solution_directory/traefik-deployment-patch.json"
kubectl -n ingress-system rollout status deployment/traefik --timeout=180s
