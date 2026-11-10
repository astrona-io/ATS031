#!/usr/bin/env bash
set -euo pipefail
context="${ASTRONA_KUBE_CONTEXT:-kind-astro-ats-031-lab-020-04-01}"
if [[ "$(kubectl config current-context)" != "$context" ]]; then
  printf 'Refusing to operate on another Kubernetes context\n' >&2
  exit 1
fi
cluster="${ASTRONA_KIND_CLUSTER:-astro-ats-031-lab-020-04-01}"
engine="${ASTRONA_CONTAINER_ENGINE:-podman}"
env_directory="$(cd "$(dirname "$0")/.." && pwd)"
node_name="$cluster-control-plane"
worker_name="$cluster-worker"
kubectl apply -f "$env_directory/bootstrap/manifests/start.yaml"
kubectl -n starfleet-031-020-04-01 rollout status deployment/probe --timeout=180s
kubectl -n starfleet-031-020-04-01 wait --for=condition=Ready pod/shuttle --timeout=120s
kubectl -n outpost-031-020-04-01 wait --for=condition=Ready pod/drifter --timeout=120s
"$engine" exec "$node_name" mkdir -p /opt/training/backup
"$engine" exec "$node_name" cp /etc/kubernetes/manifests/kube-apiserver.yaml /etc/kubernetes/manifests/etcd.yaml /opt/training/backup/
"$engine" exec "$worker_name" mkdir -p /opt/training/backup
"$engine" exec "$worker_name" cp /var/lib/kubelet/config.yaml /opt/training/backup/kubelet-config.yaml
if [[ -n "${KUBE_BENCH_DIR:-}" && -d "$KUBE_BENCH_DIR" ]]; then
  "$engine" cp "$KUBE_BENCH_DIR" "$worker_name:/opt/training/kube-bench"
fi
"$engine" exec "$node_name" chmod 755 /var/lib/etcd
