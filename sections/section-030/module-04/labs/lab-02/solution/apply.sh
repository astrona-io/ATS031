#!/usr/bin/env bash
set -euo pipefail
context="${ASTRONA_KUBE_CONTEXT:-kind-astro-ats-031-lab-030-04-02}"
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
  kubectl -n starfleet-031-030-04-02 create secret tls "$1" --cert="$certificate_directory/$1.crt" --key="$certificate_directory/$1.key"
}
kubectl -n starfleet-031-030-04-02 patch ingress alpha --type=json -p '[{"op":"replace","path":"/spec/tls/0/secretName","value":"alpha-cert"}]'
kubectl -n starfleet-031-030-04-02 delete secret bravo-tls
make_secret bravo-tls bravo.example.test
kubectl -n starfleet-031-030-04-02 patch ingress charlie --type=json -p '[{"op":"replace","path":"/spec/rules/0/host","value":"charlie.example.test"}]'
kubectl -n starfleet-031-030-04-02 patch ingress delta --type=json -p '[{"op":"replace","path":"/spec/ingressClassName","value":"traefik"}]'
