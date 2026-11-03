#!/usr/bin/env bash
set -euo pipefail
if [[ "$(kubectl config current-context)" != "kind-astro-ats-031-lab-030-03-02" ]]; then
  printf 'Refusing to operate on another Kubernetes context\n' >&2
  exit 1
fi
lab_directory="$(cd "$(dirname "$0")/.." && pwd)"
kubectl apply -f "$lab_directory/bootstrap/manifests/start.yaml"
kubectl -n starfleet rollout status deployment/probe --timeout=180s
kubectl -n starfleet rollout status deployment/scout --timeout=180s
kubectl -n starfleet rollout status deployment/beacon --timeout=180s
kubectl -n ingress-system rollout status deployment/traefik --timeout=180s
certificate_directory="$(mktemp -d)"
trap 'rm -rf "$certificate_directory"' EXIT

make_certificate() {
  # make_certificate <file name> <host name> <days> [with_san]
  local san_option=()
  if [[ "${4:-with_san}" == "with_san" ]]; then san_option=(-addext "subjectAltName=DNS:$2"); fi
  openssl req -x509 -newkey rsa:2048 -nodes -days "$3" \
    -keyout "$certificate_directory/$1.key" -out "$certificate_directory/$1.crt" \
    -subj "/CN=$2" ${san_option[@]+"${san_option[@]}"} >/dev/null 2>&1
}
make_certificate beacon beacon.example.test 30 no_san
kubectl -n outpost create secret tls beacon-tls --cert="$certificate_directory/beacon.crt" --key="$certificate_directory/beacon.key"
