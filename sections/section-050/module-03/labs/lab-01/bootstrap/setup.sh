#!/usr/bin/env bash
# Creates the lab namespace, signs a new random set of documents in a
# throwaway gpg container on the host and copies the result into the control
# plane node container. The node itself only has gpgv, which verifies.
set -euo pipefail
context="${ASTRONA_KUBE_CONTEXT:-kind-astro-ats-031-lab-050-03-01}"
if [[ "$(kubectl config current-context)" != "$context" ]]; then
  printf 'Refusing to operate on another Kubernetes context\n' >&2
  exit 1
fi
cluster="${ASTRONA_KIND_CLUSTER:-astro-ats-031-lab-050-03-01}"
engine="${ASTRONA_CONTAINER_ENGINE:-podman}"
signer_image=docker.io/library/buildpack-deps:bookworm-curl
lab_directory="$(cd "$(dirname "$0")/.." && pwd)"
kubectl apply -f "$lab_directory/bootstrap/manifests/namespace.yaml"
"$engine" image inspect "$signer_image" >/dev/null 2>&1 || "$engine" pull "$signer_image"
"$engine" exec "$cluster-control-plane" rm -rf /var/lib/doc-review
"$engine" run --rm -i --network none --entrypoint /bin/bash "$signer_image" -s < "$lab_directory/bootstrap/sign-documents.sh" \
  | "$engine" exec -i "$cluster-control-plane" tar -x -C /var/lib -f -
"$engine" exec "$cluster-control-plane" chown -R root:root /var/lib/doc-review
