#!/usr/bin/env bash
set -euo pipefail
context="${ASTRONA_KUBE_CONTEXT:-kind-astro-ats-031-lab-020-05-06}"
if [[ "$(kubectl config current-context)" != "$context" ]]; then
  printf 'Refusing to operate on another Kubernetes context\n' >&2
  exit 1
fi
cluster="${ASTRONA_KIND_CLUSTER:-astro-ats-031-lab-020-05-06}"
engine="${ASTRONA_CONTAINER_ENGINE:-podman}"
lab_directory="$(cd "$(dirname "$0")/.." && pwd)"
node_name="$cluster-control-plane"
worker_name="$cluster-worker"
namespace="starfleet-031-020-05-06"
source "$lab_directory/bootstrap/helpers.sh"
if [[ "$("$engine" inspect "$node_name" --format '{{index .Config.Labels "io.x-k8s.kind.cluster"}}')" != "$cluster" ]]; then
  printf 'Refusing to operate on an unrelated node container\n' >&2
  exit 1
fi
solution_directory="$lab_directory/solution"
kubectl -n kube-system delete rolebinding dns-maintenance
kubectl -n kube-system delete role dns-maintenance
kubectl -n kube-system get configmap coredns -o yaml | sed 's/pods insecure/pods verified/' | kubectl replace -f -
