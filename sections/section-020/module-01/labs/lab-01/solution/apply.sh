#!/usr/bin/env bash
set -euo pipefail
context="${ASTRONA_KUBE_CONTEXT:-kubernetes-admin@astro-ats-031-lab-020-01-01}"
if [[ "$(kubectl config current-context)" != "$context" ]]; then
  printf 'Refusing to operate on another Kubernetes context\n' >&2
  exit 1
fi
cluster="astro-ats-031-lab-020-01-01"
lab_directory="$(cd "$(dirname "$0")/.." && pwd)"
# The VM is the only node: control plane and worker. kubeadm names it after
# the host name, which differs under `astrona test`.
node_name="$(hostname)"
worker_name="$node_name"
namespace="starfleet-031-020-01-01"
source "$lab_directory/bootstrap/helpers.sh"
solution_directory="$lab_directory/solution"
run_on_node mkdir -p /root/backup
run_on_node cp -p /etc/kubernetes/manifests/kube-scheduler.yaml /root/backup/kube-scheduler.yaml
edit_manifest kube-scheduler 's|--bind-address=0.0.0.0|--bind-address=127.0.0.1|'
wait_for_argument "$node_name" kube-scheduler --bind-address=127.0.0.1 present
kubectl apply -f "$solution_directory/configmap-benchmark-review.yaml"
