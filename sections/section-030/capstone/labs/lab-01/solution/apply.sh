#!/usr/bin/env bash
set -euo pipefail
context="${ASTRONA_KUBE_CONTEXT:-kind-astro-ats-031-capstone-030}"
if [[ "$(kubectl config current-context)" != "$context" ]]; then
  printf 'Refusing to operate on another Kubernetes context\n' >&2
  exit 1
fi
lab_directory="$(cd "$(dirname "$0")/.." && pwd)"
solution_directory="$lab_directory/solution"
certificate_directory="$(mktemp -d)"
trap 'rm -rf "$certificate_directory"' EXIT
make_secret() {
  # make_secret <secret name> <host name>
  openssl req -x509 -newkey rsa:2048 -nodes -days 30 \
    -keyout "$certificate_directory/$1.key" -out "$certificate_directory/$1.crt" \
    -subj "/CN=$2" -addext "subjectAltName=DNS:$2" >/dev/null 2>&1
  kubectl -n starfleet create secret tls "$1" --cert="$certificate_directory/$1.crt" --key="$certificate_directory/$1.key"
}
make_secret probe-tls probe.example.test
make_secret scout-tls scout.example.test
kubectl apply -f "$solution_directory/ingress-probe.yaml"
kubectl apply -f "$solution_directory/ingress-scout.yaml"
kubectl -n ingress-system create configmap traefik-dynamic --from-file="$solution_directory/dynamic.yaml" --dry-run=client -o yaml | kubectl apply -f -
kubectl -n ingress-system patch deployment traefik --type=json --patch-file "$solution_directory/traefik-redirect-patch.json"
kubectl -n ingress-system rollout status deployment/traefik --timeout=180s
