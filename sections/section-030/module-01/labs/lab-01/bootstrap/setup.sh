#!/usr/bin/env bash
set -euo pipefail
if [[ "$(kubectl config current-context)" != "kind-astro-ats-031-lab-030-01-01" ]]; then
  printf 'Refusing to operate on another Kubernetes context\n' >&2
  exit 1
fi
lab_directory="$(cd "$(dirname "$0")/.." && pwd)"
kubectl apply -f "$lab_directory/bootstrap/manifests/start.yaml"
kubectl -n starfleet rollout status deployment/probe --timeout=180s
kubectl -n starfleet wait --for=condition=Ready pod/shuttle --timeout=120s
kubectl -n outpost wait --for=condition=Ready pod/drifter --timeout=120s
kubectl -n ingress-system rollout status deployment/traefik --timeout=180s
certificate_directory="$(mktemp -d)"
trap 'rm -rf "$certificate_directory"' EXIT
openssl req -x509 -newkey rsa:2048 -nodes -days 1 -keyout "$certificate_directory/probe.key" -out "$certificate_directory/probe.crt" -subj /CN=probe.local -addext subjectAltName=DNS:probe.local >/dev/null 2>&1
kubectl -n starfleet create secret tls probe-tls --cert="$certificate_directory/probe.crt" --key="$certificate_directory/probe.key"

