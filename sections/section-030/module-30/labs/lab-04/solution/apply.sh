#!/usr/bin/env bash
set -euo pipefail
context="${ASTRONA_KUBE_CONTEXT:-kind-astro-ats-031-lab-030-03-04}"
if [[ "$(kubectl config current-context)" != "$context" ]]; then
  printf 'Refusing to operate on another Kubernetes context\n' >&2
  exit 1
fi
lab_directory="$(cd "$(dirname "$0")/.." && pwd)"
solution_directory="$lab_directory/solution"
certificate_directory="$(mktemp -d)"
trap 'rm -rf "$certificate_directory"' EXIT
kubectl -n starfleet-031-030-03-04 get secret lab-ca -o jsonpath='{.data.tls\.crt}' | base64 -d > "$certificate_directory/ca.crt"
kubectl -n starfleet-031-030-03-04 get secret lab-ca -o jsonpath='{.data.tls\.key}' | base64 -d > "$certificate_directory/ca.key"
openssl req -newkey rsa:2048 -nodes -keyout "$certificate_directory/relay.key" -out "$certificate_directory/relay.csr" \
  -subj "/CN=relay.example.test" >/dev/null 2>&1
openssl x509 -req -in "$certificate_directory/relay.csr" -CA "$certificate_directory/ca.crt" -CAkey "$certificate_directory/ca.key" \
  -CAcreateserial -days 30 -extfile "$solution_directory/relay.ext" -out "$certificate_directory/relay.crt" >/dev/null 2>&1
kubectl -n starfleet-031-030-03-04 create secret tls relay-tls --cert="$certificate_directory/relay.crt" --key="$certificate_directory/relay.key"
