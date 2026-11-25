#!/usr/bin/env bash
set -euo pipefail
context="${ASTRONA_KUBE_CONTEXT:-kind-astro-ats-031-lab-030-01-03}"
if [[ "$(kubectl config current-context)" != "$context" ]]; then
  printf 'Refusing to operate on another Kubernetes context\n' >&2
  exit 1
fi
lab_directory="$(cd "$(dirname "$0")/.." && pwd)"
solution_directory="$lab_directory/solution"
certificate_directory="$(mktemp -d)"
trap 'rm -rf "$certificate_directory"' EXIT
make_certificate() {
  # make_certificate <file name> <host name> <days>
  openssl req -x509 -newkey rsa:2048 -nodes -days "$3" \
    -keyout "$certificate_directory/$1.key" -out "$certificate_directory/$1.crt" \
    -subj "/CN=$2" -addext "subjectAltName=DNS:$2" >/dev/null 2>&1
}
openssl req -x509 -newkey rsa:2048 -nodes -days 90 \
  -keyout "$certificate_directory/vault.key" -out "$certificate_directory/vault.crt" \
  -subj "/CN=vault.local" -addext "subjectAltName=DNS:vault.local" >/dev/null 2>&1
kubectl -n starfleet-031-030-01-03 create secret tls vault-tls --cert="$certificate_directory/vault.crt" --key="$certificate_directory/vault.key"
