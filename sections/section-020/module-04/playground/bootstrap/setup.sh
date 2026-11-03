#!/usr/bin/env bash
set -euo pipefail
if [[ "$(kubectl config current-context)" != "kind-astro-ats-031-playground-020-04" ]]; then
  printf 'Refusing to operate on another Kubernetes context\n' >&2
  exit 1
fi
env_directory="$(cd "$(dirname "$0")/.." && pwd)"
node_name="astro-ats-031-playground-020-04-control-plane"
worker_name="astro-ats-031-playground-020-04-worker"
kubectl apply -f "$env_directory/bootstrap/manifests/start.yaml"
kubectl -n starfleet rollout status deployment/probe --timeout=180s
kubectl -n starfleet wait --for=condition=Ready pod/shuttle --timeout=120s
kubectl -n outpost wait --for=condition=Ready pod/drifter --timeout=120s
podman exec "$node_name" mkdir -p /opt/training/backup
podman exec "$node_name" cp /etc/kubernetes/manifests/kube-apiserver.yaml /etc/kubernetes/manifests/etcd.yaml /opt/training/backup/
podman exec "$worker_name" mkdir -p /opt/training/backup
podman exec "$worker_name" cp /var/lib/kubelet/config.yaml /opt/training/backup/kubelet-config.yaml
if [[ -n "${KUBE_BENCH_DIR:-}" && -d "$KUBE_BENCH_DIR" ]]; then
  podman cp "$KUBE_BENCH_DIR" "$worker_name:/opt/training/kube-bench"
fi
podman exec "$node_name" chmod 755 /var/lib/etcd
