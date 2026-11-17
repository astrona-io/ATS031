#!/usr/bin/env bash
set -euo pipefail
context="${ASTRONA_KUBE_CONTEXT:-kind-astro-ats-031-lab-020-03-04}"
if [[ "$(kubectl config current-context)" != "$context" ]]; then
  printf 'Refusing to operate on another Kubernetes context\n' >&2
  exit 1
fi
cluster="${ASTRONA_KIND_CLUSTER:-astro-ats-031-lab-020-03-04}"
engine="${ASTRONA_CONTAINER_ENGINE:-podman}"
lab_directory="$(cd "$(dirname "$0")/.." && pwd)"
node_name="$cluster-control-plane"
worker_name="$cluster-worker"
namespace="starfleet-031-020-03-04"
source "$lab_directory/bootstrap/helpers.sh"
if [[ "$("$engine" inspect "$node_name" --format '{{index .Config.Labels "io.x-k8s.kind.cluster"}}')" != "$cluster" ]]; then
  printf 'Refusing to operate on an unrelated node container\n' >&2
  exit 1
fi
solution_directory="$lab_directory/solution"
edit_manifest kube-apiserver 's|--authorization-mode=AlwaysAllow|--authorization-mode=Node,RBAC|'
wait_for_argument "$node_name" kube-apiserver --authorization-mode=Node,RBAC present
wait_for_api
for binding in $(kubectl get clusterrolebindings -o jsonpath='{range .items[?(@.subjects[0].name=="system:anonymous")]}{.metadata.name}{"\n"}{end}'); do
  kubectl delete clusterrolebinding "$binding"
done
