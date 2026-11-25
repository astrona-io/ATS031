#!/usr/bin/env bash
set -euo pipefail
context="${ASTRONA_KUBE_CONTEXT:-kind-astro-ats-031-lab-030-04-03}"
if [[ "$(kubectl config current-context)" != "$context" ]]; then
  printf 'Refusing to operate on another Kubernetes context\n' >&2
  exit 1
fi
lab_directory="$(cd "$(dirname "$0")/.." && pwd)"
solution_directory="$lab_directory/solution"
certificate_directory="$(mktemp -d)"
trap 'rm -rf "$certificate_directory"' EXIT
kubectl -n starfleet-031-030-04-03 get secret crew-client -o jsonpath='{.data.ca\.crt}' | base64 -d > "$certificate_directory/client-ca.crt"
kubectl -n ingress-system create configmap client-ca --from-file=client-ca.crt="$certificate_directory/client-ca.crt"
kubectl -n ingress-system create configmap traefik-dynamic --from-file="$solution_directory/dynamic.yaml" --dry-run=client -o yaml | kubectl apply -f -
kubectl apply -f "$solution_directory/ingress-vault.yaml"
kubectl -n ingress-system rollout restart deployment/traefik
kubectl -n ingress-system rollout status deployment/traefik --timeout=180s
