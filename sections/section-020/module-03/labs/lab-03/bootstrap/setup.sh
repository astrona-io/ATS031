#!/usr/bin/env bash
set -euo pipefail
context="${ASTRONA_KUBE_CONTEXT:-kind-astro-ats-031-lab-020-03-03}"
if [[ "$(kubectl config current-context)" != "$context" ]]; then
  printf 'Refusing to operate on another Kubernetes context\n' >&2
  exit 1
fi
cluster="${ASTRONA_KIND_CLUSTER:-astro-ats-031-lab-020-03-03}"
engine="${ASTRONA_CONTAINER_ENGINE:-podman}"
lab_directory="$(cd "$(dirname "$0")/.." && pwd)"
node_name="$cluster-control-plane"
worker_name="$cluster-worker"
namespace="starfleet-031-020-03-03"
source "$lab_directory/bootstrap/helpers.sh"
if [[ "$("$engine" inspect "$node_name" --format '{{index .Config.Labels "io.x-k8s.kind.cluster"}}')" != "$cluster" ]]; then
  printf 'Refusing to operate on an unrelated node container\n' >&2
  exit 1
fi
kubectl apply -f "$lab_directory/bootstrap/manifests/start.yaml"
kubectl -n starfleet-031-020-03-03 rollout status deployment/probe --timeout=180s
kubectl -n starfleet-031-020-03-03 wait --for=condition=Ready pod/shuttle --timeout=120s
kubectl -n outpost-031-020-03-03 wait --for=condition=Ready pod/drifter --timeout=120s
run_on_node mkdir -p /opt/training/backup
run_on_node cp /etc/kubernetes/manifests/kube-controller-manager.yaml /opt/training/backup/kube-controller-manager.yaml
run_on_node chmod 644 /opt/training/backup/kube-controller-manager.yaml
edit_manifest kube-controller-manager 's|^\( *\)- --bind-address=127.0.0.1$|&\n\1- --profilling=false|'
run_on_node chmod 644 /etc/kubernetes/manifests/kube-controller-manager.yaml
for attempt in $(seq 1 60); do
  arguments="$(process_arguments "$node_name" kube-controller-manager)"
  if [[ -z "$arguments" ]] || grep -qxF -- --profilling=false <<<"$arguments"; then
    break
  fi
  sleep 3
done
# The broken process exits at once; wait until the pod status shows it, so a
# stale Ready status cannot hide the fault from the reference solution.
wait_for_pod_ready "kube-controller-manager-$node_name" False
