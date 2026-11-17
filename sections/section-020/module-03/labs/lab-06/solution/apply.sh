#!/usr/bin/env bash
set -euo pipefail
context="${ASTRONA_KUBE_CONTEXT:-kind-astro-ats-031-lab-020-03-06}"
if [[ "$(kubectl config current-context)" != "$context" ]]; then
  printf 'Refusing to operate on another Kubernetes context\n' >&2
  exit 1
fi
cluster="${ASTRONA_KIND_CLUSTER:-astro-ats-031-lab-020-03-06}"
engine="${ASTRONA_CONTAINER_ENGINE:-podman}"
lab_directory="$(cd "$(dirname "$0")/.." && pwd)"
node_name="$cluster-control-plane"
worker_name="$cluster-worker"
namespace="starfleet-031-020-03-06"
source "$lab_directory/bootstrap/helpers.sh"
if [[ "$("$engine" inspect "$node_name" --format '{{index .Config.Labels "io.x-k8s.kind.cluster"}}')" != "$cluster" ]]; then
  printf 'Refusing to operate on an unrelated node container\n' >&2
  exit 1
fi
solution_directory="$lab_directory/solution"
edit_manifest kube-controller-manager 's|^\( *\)- kube-controller-manager$|&\n\1- --profiling=false|'
edit_manifest kube-scheduler 's|^\( *\)- kube-scheduler$|&\n\1- --profiling=false|'
run_on_node sh -c 'chmod 600 /etc/kubernetes/manifests/*.yaml'
wait_for_argument "$node_name" kube-controller-manager --profiling=false present
wait_for_argument "$node_name" kube-scheduler --profiling=false present
kubectl -n kube-system wait --for=condition=Ready "pod/kube-controller-manager-$node_name" "pod/kube-scheduler-$node_name" --timeout=180s
