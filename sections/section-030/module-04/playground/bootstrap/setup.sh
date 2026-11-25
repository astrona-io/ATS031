#!/usr/bin/env bash
set -euo pipefail
if [[ "$(kubectl config current-context)" != "kind-astro-ats-031-playground-030-04" ]]; then
  printf 'Refusing to operate on another Kubernetes context\n' >&2
  exit 1
fi
lab_directory="$(cd "$(dirname "$0")/.." && pwd)"
kubectl apply -f "$lab_directory/bootstrap/manifests/start.yaml"
kubectl -n starfleet rollout status deployment/probe --timeout=180s
kubectl -n starfleet rollout status deployment/scout --timeout=180s
kubectl -n starfleet wait --for=condition=Ready pod/shuttle --timeout=120s
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
make_certificate probe probe.example.test 1
kubectl -n starfleet create secret tls probe-tls --cert="$certificate_directory/probe.crt" --key="$certificate_directory/probe.key"

# case-one: the Ingress names one-tls, the working Secret is one-cert
make_certificate one one.example.test 30
kubectl -n starfleet create secret tls one-cert --cert="$certificate_directory/one.crt" --key="$certificate_directory/one.key"

# case-two: certificate and key come from two different pairs
make_certificate two two.example.test 30
make_certificate spare spare.example.test 30
kubectl -n starfleet create secret generic two-tls --type=kubernetes.io/tls \
  --from-file=tls.crt="$certificate_directory/two.crt" --from-file=tls.key="$certificate_directory/spare.key"

# case-three and case-four: the Secrets are fine, the Ingress objects are wrong
make_certificate three three.example.test 30
kubectl -n starfleet create secret tls three-tls --cert="$certificate_directory/three.crt" --key="$certificate_directory/three.key"
make_certificate four four.example.test 30
kubectl -n starfleet create secret tls four-tls --cert="$certificate_directory/four.crt" --key="$certificate_directory/four.key"
