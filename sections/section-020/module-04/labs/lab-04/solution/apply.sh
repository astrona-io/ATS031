#!/usr/bin/env bash
set -euo pipefail
context="${ASTRONA_KUBE_CONTEXT:-kubernetes-admin@astro-ats-031-lab-020-04-04}"
if [[ "$(kubectl config current-context)" != "$context" ]]; then
  printf 'Refusing to operate on another Kubernetes context\n' >&2
  exit 1
fi
cluster="astro-ats-031-lab-020-04-04"
lab_directory="$(cd "$(dirname "$0")/.." && pwd)"
# The VM is the only node: control plane and worker. kubeadm names it after
# the host name, which differs under `astrona test`.
node_name="$(hostname)"
worker_name="$node_name"
namespace="starfleet-031-020-04-04"
source "$lab_directory/bootstrap/helpers.sh"
solution_directory="$lab_directory/solution"
data_directory="$(process_arguments "$node_name" etcd | grep -E '^--data-dir=' | tail -n 1 | cut -d= -f2-)"
run_on_node chmod 700 "$data_directory"
process_user="$(run_on_node ps -o user= -p "$(run_on_node pgrep -n -f '^(/[^ ]*/)?etcd( |$)')" | tr -d ' ')"
kubectl -n "$namespace" create configmap etcd-process --from-literal=data-dir="$data_directory" --from-literal=user="$process_user" --dry-run=client -o yaml | kubectl apply -f -
