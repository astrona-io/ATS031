#!/usr/bin/env bash
set -euo pipefail
context="${ASTRONA_KUBE_CONTEXT:-kubernetes-admin@astro-ats-031-lab-020-03-04}"
if [[ "$(kubectl config current-context)" != "$context" ]]; then
  printf 'Refusing to operate on another Kubernetes context\n' >&2
  exit 1
fi
cluster="astro-ats-031-lab-020-03-04"
lab_directory="$(cd "$(dirname "$0")/.." && pwd)"
# The VM is the only node: control plane and worker. kubeadm names it after
# the host name, which differs under `astrona test`.
node_name="$(hostname)"
worker_name="$node_name"
namespace="starfleet-031-020-03-04"
source "$lab_directory/bootstrap/helpers.sh"
solution_directory="$lab_directory/solution"
edit_manifest kube-apiserver 's|--authorization-mode=AlwaysAllow|--authorization-mode=Node,RBAC|'
wait_for_argument "$node_name" kube-apiserver --authorization-mode=Node,RBAC present
wait_for_api
for binding in $(kubectl get clusterrolebindings -o jsonpath='{range .items[?(@.subjects[0].name=="system:anonymous")]}{.metadata.name}{"\n"}{end}'); do
  kubectl delete clusterrolebinding "$binding"
done
