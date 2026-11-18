#!/usr/bin/env bash
set -euo pipefail
context="${ASTRONA_KUBE_CONTEXT:-kubernetes-admin@astro-ats-031-lab-020-01-02}"
if [[ "$(kubectl config current-context)" != "$context" ]]; then
  printf 'Refusing to operate on another Kubernetes context\n' >&2
  exit 1
fi
cluster="astro-ats-031-lab-020-01-02"
lab_directory="$(cd "$(dirname "$0")/.." && pwd)"
# The VM is the only node: control plane and worker. kubeadm names it after
# the host name, which differs under `astrona test`.
node_name="$(hostname)"
worker_name="$node_name"
namespace="starfleet-031-020-01-02"
source "$lab_directory/bootstrap/helpers.sh"
solution_directory="$lab_directory/solution"
run_on_node sh -c 'chmod 600 /etc/kubernetes/*.conf'
run_on_node find /etc/kubernetes/pki -name '*.key' -exec chmod 600 {} +
