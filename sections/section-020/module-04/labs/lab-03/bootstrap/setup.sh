#!/usr/bin/env bash
# Runs inside the lab VM from /opt/astrona-lab after vm/install.sh built the cluster.
set -euo pipefail
context="${ASTRONA_KUBE_CONTEXT:-kubernetes-admin@astro-ats-031-lab-020-04-03}"
if [[ "$(kubectl config current-context)" != "$context" ]]; then
  printf 'Refusing to operate on another Kubernetes context\n' >&2
  exit 1
fi
cluster="astro-ats-031-lab-020-04-03"
lab_directory="$(cd "$(dirname "$0")/.." && pwd)"
# The VM is the only node: control plane and worker. kubeadm names it after
# the host name, which differs under `astrona test`.
node_name="$(hostname)"
worker_name="$node_name"
namespace="starfleet-031-020-04-03"
source "$lab_directory/bootstrap/helpers.sh"
kubectl apply -f "$lab_directory/bootstrap/manifests/start.yaml"
kubectl -n starfleet-031-020-04-03 rollout status deployment/probe --timeout=180s
kubectl -n starfleet-031-020-04-03 wait --for=condition=Ready pod/shuttle --timeout=120s
kubectl -n outpost-031-020-04-03 wait --for=condition=Ready pod/drifter --timeout=120s
run_on_node mkdir -p /opt/training/backup
run_on_node cp /etc/kubernetes/manifests/etcd.yaml /opt/training/backup/etcd.yaml
edit_manifest etcd 's|^\( *\)- --client-cert-auth=true$|\1- --client-cert-auth=false|; s|^\( *\)- --peer-client-cert-auth=true$|\1- --peer-client-cert-auth=false|'
wait_for_argument "$node_name" etcd --client-cert-auth=false present
wait_for_api
