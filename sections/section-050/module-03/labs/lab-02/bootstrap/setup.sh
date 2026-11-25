#!/usr/bin/env bash
# Creates the lab namespace, builds and signs a new flat apt repository in a
# throwaway container on the host, copies it into the control plane node
# container and runs bootstrap/stage-node.sh there.
set -euo pipefail
context="${ASTRONA_KUBE_CONTEXT:-kind-astro-ats-031-lab-050-03-02}"
if [[ "$(kubectl config current-context)" != "$context" ]]; then
  printf 'Refusing to operate on another Kubernetes context\n' >&2
  exit 1
fi
cluster="${ASTRONA_KIND_CLUSTER:-astro-ats-031-lab-050-03-02}"
engine="${ASTRONA_CONTAINER_ENGINE:-podman}"
builder_image=docker.io/library/buildpack-deps:bookworm-curl
lab_directory="$(cd "$(dirname "$0")/.." && pwd)"
kubectl apply -f "$lab_directory/bootstrap/manifests/namespace.yaml"
"$engine" image inspect "$builder_image" >/dev/null 2>&1 || "$engine" pull "$builder_image"
"$engine" exec "$cluster-control-plane" rm -rf /var/lib/fleet-apt
"$engine" run --rm -i --network none --entrypoint /bin/bash "$builder_image" -s < "$lab_directory/bootstrap/build-repository.sh" \
  | "$engine" exec -i "$cluster-control-plane" tar -x -C /var/lib -f -
"$engine" exec "$cluster-control-plane" chown -R root:root /var/lib/fleet-apt
"$engine" exec -i "$cluster-control-plane" bash -s < "$lab_directory/bootstrap/stage-node.sh"
