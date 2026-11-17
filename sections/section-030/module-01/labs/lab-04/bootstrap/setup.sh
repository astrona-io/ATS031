#!/usr/bin/env bash
set -euo pipefail
context="${ASTRONA_KUBE_CONTEXT:-kind-astro-ats-031-lab-030-01-04}"
if [[ "$(kubectl config current-context)" != "$context" ]]; then
  printf 'Refusing to operate on another Kubernetes context\n' >&2
  exit 1
fi
lab_directory="$(cd "$(dirname "$0")/.." && pwd)"
kubectl apply -f "$lab_directory/bootstrap/manifests/start.yaml"
kubectl -n starfleet-031-030-01-04 rollout status deployment/probe --timeout=180s
kubectl -n starfleet-031-030-01-04 rollout status deployment/bridge --timeout=180s
kubectl -n starfleet-031-030-01-04 rollout status deployment/dock --timeout=180s
kubectl -n ingress-system rollout status deployment/traefik --timeout=180s
certificate_directory="$(mktemp -d)"
trap 'rm -rf "$certificate_directory"' EXIT
make_certificate() {
  # make_certificate <file name> <host name> <days>
  openssl req -x509 -newkey rsa:2048 -nodes -days "$3" \
    -keyout "$certificate_directory/$1.key" -out "$certificate_directory/$1.crt" \
    -subj "/CN=$2" -addext "subjectAltName=DNS:$2" >/dev/null 2>&1
}
for host in bridge dock; do
  make_certificate "$host" "$host.local" 30
  kubectl -n starfleet-031-030-01-04 create secret tls "$host-tls" --cert="$certificate_directory/$host.crt" --key="$certificate_directory/$host.key"
done
