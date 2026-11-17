#!/usr/bin/env bash
set -euo pipefail
context="${ASTRONA_KUBE_CONTEXT:-kind-astro-ats-031-lab-030-04-03}"
if [[ "$(kubectl config current-context)" != "$context" ]]; then
  printf 'Refusing to operate on another Kubernetes context\n' >&2
  exit 1
fi
lab_directory="$(cd "$(dirname "$0")/.." && pwd)"
kubectl apply -f "$lab_directory/bootstrap/manifests/start.yaml"
kubectl -n starfleet-031-030-04-03 rollout status deployment/probe --timeout=180s
kubectl -n starfleet-031-030-04-03 rollout status deployment/vault --timeout=180s
kubectl -n starfleet-031-030-04-03 rollout status deployment/beacon --timeout=180s
kubectl -n ingress-system rollout status deployment/traefik --timeout=180s
certificate_directory="$(mktemp -d)"
trap 'rm -rf "$certificate_directory"' EXIT
make_certificate() {
  # make_certificate <file name> <host name> <days>
  openssl req -x509 -newkey rsa:2048 -nodes -days "$3" \
    -keyout "$certificate_directory/$1.key" -out "$certificate_directory/$1.crt" \
    -subj "/CN=$2" -addext "subjectAltName=DNS:$2" >/dev/null 2>&1
}
make_certificate vault vault.example.test 30
make_certificate beacon beacon.example.test 30
kubectl -n starfleet-031-030-04-03 create secret tls vault-tls --cert="$certificate_directory/vault.crt" --key="$certificate_directory/vault.key"
kubectl -n starfleet-031-030-04-03 create secret tls beacon-tls --cert="$certificate_directory/beacon.crt" --key="$certificate_directory/beacon.key"
openssl req -x509 -newkey rsa:2048 -nodes -days 30 \
  -keyout "$certificate_directory/crew-ca.key" -out "$certificate_directory/crew-ca.crt" -subj "/CN=crew-ca" >/dev/null 2>&1
openssl req -newkey rsa:2048 -nodes -keyout "$certificate_directory/crew.key" -out "$certificate_directory/crew.csr" \
  -subj "/CN=ensign-two" >/dev/null 2>&1
openssl x509 -req -in "$certificate_directory/crew.csr" -CA "$certificate_directory/crew-ca.crt" -CAkey "$certificate_directory/crew-ca.key" \
  -CAcreateserial -days 30 -out "$certificate_directory/crew.crt" >/dev/null 2>&1
kubectl -n starfleet-031-030-04-03 create secret generic crew-client --type=kubernetes.io/tls \
  --from-file=tls.crt="$certificate_directory/crew.crt" --from-file=tls.key="$certificate_directory/crew.key" \
  --from-file=ca.crt="$certificate_directory/crew-ca.crt"
