#!/usr/bin/env bash
set -euo pipefail
context="${ASTRONA_KUBE_CONTEXT:-kind-astro-ats-031-lab-020-04-02}"
if [[ "$(kubectl config current-context)" != "$context" ]]; then
  printf 'Refusing to operate on another Kubernetes context\n' >&2
  exit 1
fi
cluster="${ASTRONA_KIND_CLUSTER:-astro-ats-031-lab-020-04-02}"
engine="${ASTRONA_CONTAINER_ENGINE:-podman}"
lab_directory="$(cd "$(dirname "$0")/.." && pwd)"
node_name="$cluster-control-plane"
worker_name="$cluster-worker"
namespace="starfleet-031-020-04-02"
source "$lab_directory/bootstrap/helpers.sh"
if [[ "$("$engine" inspect "$node_name" --format '{{index .Config.Labels "io.x-k8s.kind.cluster"}}')" != "$cluster" ]]; then
  printf 'Refusing to operate on an unrelated node container\n' >&2
  exit 1
fi
solution_directory="$lab_directory/solution"
arguments="$(process_arguments "$node_name" kube-apiserver)"
flag() { grep -E "^--$1=" <<<"$arguments" | tail -n 1 | cut -d= -f2-; }
kubectl -n "$namespace" create configmap etcd-connection \
  --from-literal=servers="$(flag etcd-servers)" \
  --from-literal=client-certificate="$(flag etcd-certfile)" \
  --from-literal=client-key="$(flag etcd-keyfile)" \
  --from-literal=ca-file="$(flag etcd-cafile)" \
  --dry-run=client -o yaml | kubectl apply -f -
