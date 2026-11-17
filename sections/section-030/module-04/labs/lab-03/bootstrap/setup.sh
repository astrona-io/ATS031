#!/usr/bin/env bash
set -euo pipefail
context="${ASTRONA_KUBE_CONTEXT:-kind-astro-ats-031-lab-030-04-03}"
cluster="${ASTRONA_KIND_CLUSTER:-astro-ats-031-lab-030-04-03}"
engine="${ASTRONA_CONTAINER_ENGINE:-podman}"
[[ "$(kubectl config current-context)" == "$context" ]] || { echo 'ERROR: wrong context'; exit 2; }
lab_directory="$(cd "$(dirname "$0")/.." && pwd)"
kubectl apply -f "$lab_directory/bootstrap/start.yaml"
kubectl -n rotation-training rollout status deployment/probe --timeout=180s
kubectl -n ingress-system rollout status deployment/traefik --timeout=180s
certs=$(mktemp -d)
trap 'rm -rf "$certs"' EXIT
openssl req -x509 -newkey rsa:2048 -nodes -days 3 -keyout "$certs/ca.key" -out "$certs/ca.crt" -subj /CN=TrainingRoot -addext 'basicConstraints=critical,CA:TRUE' -addext 'keyUsage=critical,keyCertSign,cRLSign' -addext 'subjectKeyIdentifier=hash' >/dev/null 2>&1
printf 'subjectAltName=DNS:probe.example.test\nbasicConstraints=critical,CA:FALSE\nkeyUsage=critical,digitalSignature,keyEncipherment\nextendedKeyUsage=serverAuth\nsubjectKeyIdentifier=hash\nauthorityKeyIdentifier=keyid,issuer\n' > "$certs/extensions"
for version in old next; do
  openssl req -new -newkey rsa:2048 -nodes -keyout "$certs/$version.key" -out "$certs/$version.csr" -subj /CN=probe.example.test >/dev/null 2>&1
  openssl x509 -req -in "$certs/$version.csr" -CA "$certs/ca.crt" -CAkey "$certs/ca.key" -CAcreateserial -days 2 -extfile "$certs/extensions" -out "$certs/$version.crt" >/dev/null 2>&1
  kubectl -n rotation-training create secret tls "probe-$version" --cert="$certs/$version.crt" --key="$certs/$version.key"
done
kubectl -n rotation-training create secret tls probe-tls --cert="$certs/old.crt" --key="$certs/old.key"
kubectl -n rotation-training create configmap rotation-trust --from-file=ca.crt="$certs/ca.crt"
