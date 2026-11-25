#!/usr/bin/env bash
# Runs inside the lab VM from /opt/astrona-lab after vm/install.sh built the cluster.
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
kubectl apply -f "$lab_directory/bootstrap/manifests/start.yaml"
kubectl -n starfleet-031-020-01-01 rollout status deployment/probe --timeout=180s
kubectl -n starfleet-031-020-01-01 wait --for=condition=Ready pod/shuttle --timeout=120s
kubectl -n outpost-031-020-01-01 wait --for=condition=Ready pod/drifter --timeout=120s
edit_manifest kube-scheduler 's|--bind-address=127.0.0.1|--bind-address=0.0.0.0|'
wait_for_argument "$node_name" kube-scheduler --bind-address=0.0.0.0 present
