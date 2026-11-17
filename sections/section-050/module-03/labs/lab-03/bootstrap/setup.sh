#!/usr/bin/env bash
# Creates the lab namespace, copies the cosign binary from the official cosign
# image into the control plane node container and runs bootstrap/stage-node.sh
# there to sign and damage a new set of build records.
set -euo pipefail
context="${ASTRONA_KUBE_CONTEXT:-kind-astro-ats-031-lab-050-03-03}"
if [[ "$(kubectl config current-context)" != "$context" ]]; then
  printf 'Refusing to operate on another Kubernetes context\n' >&2
  exit 1
fi
cluster="${ASTRONA_KIND_CLUSTER:-astro-ats-031-lab-050-03-03}"
engine="${ASTRONA_CONTAINER_ENGINE:-podman}"
cosign_image=ghcr.io/sigstore/cosign/cosign:v2.4.1
lab_directory="$(cd "$(dirname "$0")/.." && pwd)"
kubectl apply -f "$lab_directory/bootstrap/manifests/namespace.yaml"
"$engine" image inspect "$cosign_image" >/dev/null 2>&1 || "$engine" pull "$cosign_image"
cosign_container="$("$engine" create "$cosign_image")"
"$engine" cp "$cosign_container:/ko-app/cosign" - | "$engine" exec -i "$cluster-control-plane" tar -x -C /usr/local/bin -f -
"$engine" rm "$cosign_container" >/dev/null
"$engine" exec "$cluster-control-plane" chown root:root /usr/local/bin/cosign
"$engine" exec -i "$cluster-control-plane" bash -s < "$lab_directory/bootstrap/stage-node.sh"
