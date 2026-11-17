#!/usr/bin/env bash
set -euo pipefail
context="${ASTRONA_KUBE_CONTEXT:-kind-astro-ats-031-lab-020-05-05}"
if [[ "$(kubectl config current-context)" != "$context" ]]; then
  printf 'Refusing to operate on another Kubernetes context\n' >&2
  exit 1
fi
cluster="${ASTRONA_KIND_CLUSTER:-astro-ats-031-lab-020-05-05}"
engine="${ASTRONA_CONTAINER_ENGINE:-podman}"
lab_directory="$(cd "$(dirname "$0")/.." && pwd)"
node_name="$cluster-control-plane"
worker_name="$cluster-worker"
namespace="starfleet-031-020-05-05"
source "$lab_directory/bootstrap/helpers.sh"
if [[ "$("$engine" inspect "$node_name" --format '{{index .Config.Labels "io.x-k8s.kind.cluster"}}')" != "$cluster" ]]; then
  printf 'Refusing to operate on an unrelated node container\n' >&2
  exit 1
fi
kubectl apply -f "$lab_directory/bootstrap/manifests/start.yaml"
kubectl -n starfleet-031-020-05-05 rollout status deployment/probe --timeout=180s
kubectl -n starfleet-031-020-05-05 wait --for=condition=Ready pod/shuttle --timeout=120s
kubectl -n outpost-031-020-05-05 wait --for=condition=Ready pod/drifter --timeout=120s
run_on_worker mkdir -p /opt/training/backup
run_on_worker cp /var/lib/kubelet/config.yaml /opt/training/backup/kubelet-config.yaml

unit_files="$(run_on_worker systemctl show kubelet -p FragmentPath -p DropInPaths --value | tr ' ' '\n' | grep '^/')"
while read -r unit_file; do
  run_on_worker chmod 644 "$unit_file"
done <<<"$unit_files"
set_kubelet_field rotateCertificates false
run_on_worker systemctl restart kubelet
wait_for_configz '"rotateCertificates":true' absent
wait_for_worker
