#!/usr/bin/env bash
# Creates the lab namespace and stages a new random starting state inside the
# lab's worker node container. The staging script is bootstrap/stage-node.sh.
set -euo pipefail
context="${ASTRONA_KUBE_CONTEXT:-kind-astro-ats-031-lab-050-02-05}"
if [[ "$(kubectl config current-context)" != "$context" ]]; then
  printf 'Refusing to operate on another Kubernetes context\n' >&2
  exit 1
fi
cluster="${ASTRONA_KIND_CLUSTER:-astro-ats-031-lab-050-02-05}"
engine="${ASTRONA_CONTAINER_ENGINE:-podman}"
lab_directory="$(cd "$(dirname "$0")/.." && pwd)"
kubectl apply -f "$lab_directory/bootstrap/manifests/namespace.yaml"
"$engine" exec -i "$cluster-worker" bash -s < "$lab_directory/bootstrap/stage-node.sh"
kubectl wait --for=condition=Ready "node/$cluster-worker" --timeout=180s
