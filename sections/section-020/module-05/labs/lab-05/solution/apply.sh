#!/usr/bin/env bash
set -euo pipefail
context="${ASTRONA_KUBE_CONTEXT:-kubernetes-admin@astro-ats-031-lab-020-05-05}"
if [[ "$(kubectl config current-context)" != "$context" ]]; then
  printf 'Refusing to operate on another Kubernetes context\n' >&2
  exit 1
fi
cluster="astro-ats-031-lab-020-05-05"
lab_directory="$(cd "$(dirname "$0")/.." && pwd)"
# The VM is the only node: control plane and worker. kubeadm names it after
# the host name, which differs under `astrona test`.
node_name="$(hostname)"
worker_name="$node_name"
namespace="starfleet-031-020-05-05"
source "$lab_directory/bootstrap/helpers.sh"
solution_directory="$lab_directory/solution"
unit_files="$(run_on_worker systemctl show kubelet -p FragmentPath -p DropInPaths --value | tr ' ' '\n' | grep '^/')"
while read -r unit_file; do
  run_on_worker chmod 600 "$unit_file"
done <<<"$unit_files"
set_kubelet_field rotateCertificates true
run_on_worker systemctl restart kubelet
wait_for_configz '"rotateCertificates":true'
wait_for_worker
