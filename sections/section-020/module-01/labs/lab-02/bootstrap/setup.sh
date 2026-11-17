#!/usr/bin/env bash
set -euo pipefail
context="${ASTRONA_KUBE_CONTEXT:-kind-astro-ats-031-lab-020-01-02}"
if [[ "$(kubectl config current-context)" != "$context" ]]; then
  printf 'Refusing to operate on another Kubernetes context\n' >&2
  exit 1
fi
cluster="${ASTRONA_KIND_CLUSTER:-astro-ats-031-lab-020-01-02}"
engine="${ASTRONA_CONTAINER_ENGINE:-podman}"
lab_directory="$(cd "$(dirname "$0")/.." && pwd)"
node_name="$cluster-control-plane"
worker_name="$cluster-worker"
namespace="starfleet-031-020-01-02"
source "$lab_directory/bootstrap/helpers.sh"
if [[ "$("$engine" inspect "$node_name" --format '{{index .Config.Labels "io.x-k8s.kind.cluster"}}')" != "$cluster" ]]; then
  printf 'Refusing to operate on an unrelated node container\n' >&2
  exit 1
fi
kubectl apply -f "$lab_directory/bootstrap/manifests/start.yaml"
kubectl -n starfleet-031-020-01-02 rollout status deployment/probe --timeout=180s
kubectl -n starfleet-031-020-01-02 wait --for=condition=Ready pod/shuttle --timeout=120s
kubectl -n outpost-031-020-01-02 wait --for=condition=Ready pod/drifter --timeout=120s
run_on_node chmod 644 /etc/kubernetes/admin.conf /etc/kubernetes/scheduler.conf
run_on_node chmod 644 /etc/kubernetes/pki/apiserver.key /etc/kubernetes/pki/sa.key /etc/kubernetes/pki/etcd/peer.key
