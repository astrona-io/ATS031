#!/usr/bin/env bash
set -euo pipefail
context="${ASTRONA_KUBE_CONTEXT:-kubernetes-admin@astro-ats-031-lab-020-03-06}"
if [[ "$(kubectl config current-context)" != "$context" ]]; then
  printf 'Refusing to operate on another Kubernetes context\n' >&2
  exit 1
fi
cluster="astro-ats-031-lab-020-03-06"
lab_directory="$(cd "$(dirname "$0")/.." && pwd)"
# The VM is the only node: control plane and worker. kubeadm names it after
# the host name, which differs under `astrona test`.
node_name="$(hostname)"
worker_name="$node_name"
namespace="starfleet-031-020-03-06"
source "$lab_directory/bootstrap/helpers.sh"
solution_directory="$lab_directory/solution"
edit_manifest kube-controller-manager 's|^\( *\)- kube-controller-manager$|&\n\1- --profiling=false|'
edit_manifest kube-scheduler 's|^\( *\)- kube-scheduler$|&\n\1- --profiling=false|'
run_on_node sh -c 'chmod 600 /etc/kubernetes/manifests/*.yaml'
wait_for_argument "$node_name" kube-controller-manager --profiling=false present
wait_for_argument "$node_name" kube-scheduler --profiling=false present
kubectl -n kube-system wait --for=condition=Ready "pod/kube-controller-manager-$node_name" "pod/kube-scheduler-$node_name" --timeout=180s
