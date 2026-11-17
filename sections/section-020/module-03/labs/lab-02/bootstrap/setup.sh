#!/usr/bin/env bash
set -euo pipefail
context="${ASTRONA_KUBE_CONTEXT:-kind-astro-ats-031-lab-020-03-02}"
if [[ "$(kubectl config current-context)" != "$context" ]]; then
  printf 'Refusing to operate on another Kubernetes context\n' >&2
  exit 1
fi
cluster="${ASTRONA_KIND_CLUSTER:-astro-ats-031-lab-020-03-02}"
engine="${ASTRONA_CONTAINER_ENGINE:-podman}"
lab_directory="$(cd "$(dirname "$0")/.." && pwd)"
node_name="$cluster-control-plane"
worker_name="$cluster-worker"
namespace="starfleet-031-020-03-02"
source "$lab_directory/bootstrap/helpers.sh"
if [[ "$("$engine" inspect "$node_name" --format '{{index .Config.Labels "io.x-k8s.kind.cluster"}}')" != "$cluster" ]]; then
  printf 'Refusing to operate on an unrelated node container\n' >&2
  exit 1
fi
kubectl apply -f "$lab_directory/bootstrap/manifests/start.yaml"
kubectl -n starfleet-031-020-03-02 rollout status deployment/probe --timeout=180s
kubectl -n starfleet-031-020-03-02 wait --for=condition=Ready pod/shuttle --timeout=120s
kubectl -n outpost-031-020-03-02 wait --for=condition=Ready pod/drifter --timeout=120s
edit_manifest kube-apiserver 's|^\( *\)- kube-apiserver$|&\n\1- --tls-min-version=VersionTLS10|'
wait_for_argument "$node_name" kube-apiserver --tls-min-version=VersionTLS10 present
wait_for_api
