#!/usr/bin/env bash
set -euo pipefail
context="${ASTRONA_KUBE_CONTEXT:-kind-astro-ats-031-lab-030-03-05}"
if [[ "$(kubectl config current-context)" != "$context" ]]; then
  printf 'Refusing to operate on another Kubernetes context\n' >&2
  exit 1
fi
lab_directory="$(cd "$(dirname "$0")/.." && pwd)"
kubectl apply -f "$lab_directory/bootstrap/manifests/start.yaml"
kubectl -n starfleet-031-030-03-05 rollout status deployment/probe --timeout=180s
kubectl -n starfleet-031-030-03-05 rollout status deployment/harbor --timeout=180s
kubectl -n ingress-system rollout status deployment/traefik --timeout=180s
certificate_directory="$(mktemp -d)"
trap 'rm -rf "$certificate_directory"' EXIT
make_certificate() {
  # make_certificate <file name> <host name> <days>
  openssl req -x509 -newkey rsa:2048 -nodes -days "$3" \
    -keyout "$certificate_directory/$1.key" -out "$certificate_directory/$1.crt" \
    -subj "/CN=$2" -addext "subjectAltName=DNS:$2" >/dev/null 2>&1
}
make_certificate harbor harbor.example.test 30
kubectl -n starfleet-031-030-03-05 create secret tls harbor-tls --cert="$certificate_directory/harbor.crt" --key="$certificate_directory/harbor.key"
