#!/usr/bin/env bash
set -euo pipefail
context="${ASTRONA_KUBE_CONTEXT:-kind-astro-ats-031-lab-030-03-04}"
if [[ "$(kubectl config current-context)" != "$context" ]]; then
  printf 'Refusing to operate on another Kubernetes context\n' >&2
  exit 1
fi
lab_directory="$(cd "$(dirname "$0")/.." && pwd)"
kubectl apply -f "$lab_directory/bootstrap/manifests/start.yaml"
kubectl -n starfleet-031-030-03-04 rollout status deployment/probe --timeout=180s
kubectl -n starfleet-031-030-03-04 rollout status deployment/relay --timeout=180s
kubectl -n ingress-system rollout status deployment/traefik --timeout=180s
certificate_directory="$(mktemp -d)"
trap 'rm -rf "$certificate_directory"' EXIT
openssl req -x509 -newkey rsa:2048 -nodes -days 365 \
  -keyout "$certificate_directory/ca.key" -out "$certificate_directory/ca.crt" \
  -subj "/CN=Starfleet Lab CA" -addext "basicConstraints=critical,CA:TRUE" -addext "keyUsage=critical,keyCertSign,cRLSign" >/dev/null 2>&1
kubectl -n starfleet-031-030-03-04 create secret tls lab-ca --cert="$certificate_directory/ca.crt" --key="$certificate_directory/ca.key"
kubectl -n starfleet-031-030-03-04 create configmap lab-ca-original --from-file=ca.crt="$certificate_directory/ca.crt"
