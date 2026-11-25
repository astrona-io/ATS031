#!/usr/bin/env bash
set -euo pipefail
context="${ASTRONA_KUBE_CONTEXT:-kubernetes-admin@astro-ats-031-lab-020-05-02}"
if [[ "$(kubectl config current-context)" != "$context" ]]; then
  printf 'Refusing to operate on another Kubernetes context\n' >&2
  exit 1
fi
cluster="astro-ats-031-lab-020-05-02"
lab_directory="$(cd "$(dirname "$0")/.." && pwd)"
# The VM is the only node: control plane and worker. kubeadm names it after
# the host name, which differs under `astrona test`.
node_name="$(hostname)"
worker_name="$node_name"
namespace="starfleet-031-020-05-02"
source "$lab_directory/bootstrap/helpers.sh"
solution_directory="$lab_directory/solution"
run_on_worker chmod 600 /var/lib/kubelet/config.yaml /etc/kubernetes/kubelet.conf
set_kubelet_field rotateCertificates true
set_kubelet_field streamingConnectionIdleTimeout 5m
set_kubelet_field tlsMinVersion VersionTLS12
run_on_worker systemctl restart kubelet
wait_for_configz '"tlsMinVersion":"VersionTLS12"'
wait_for_worker
