#!/usr/bin/env bash
set -euo pipefail
if [[ "$(kubectl config current-context)" != "kind-astro-ats-031-playground-020-03" ]]; then
  printf 'Refusing to operate on another Kubernetes context\n' >&2
  exit 1
fi
lab_directory="$(cd "$(dirname "$0")/.." && pwd)"
node_name="astro-ats-031-playground-020-03-control-plane"
worker_name="astro-ats-031-playground-020-03-worker"
kubectl apply -f "$lab_directory/bootstrap/manifests/start.yaml"
kubectl -n starfleet rollout status deployment/probe --timeout=180s
kubectl -n starfleet wait --for=condition=Ready pod/shuttle --timeout=120s
kubectl -n outpost wait --for=condition=Ready pod/drifter --timeout=120s
if [[ "$(podman inspect "$node_name" --format '{{index .Config.Labels "io.x-k8s.kind.cluster"}}')" != "astro-ats-031-playground-020-03" ]]; then
  printf 'Refusing to operate on an unrelated node container\n' >&2
  exit 1
fi
# Working copies of the original manifests, kept outside the manifests directory.
podman exec "$node_name" mkdir -p /opt/training/backup
podman exec "$node_name" sh -c 'cp -p /etc/kubernetes/manifests/*.yaml /opt/training/backup/'
# Stage an audit policy that no component references yet.
podman exec -i "$node_name" sh -c 'cat > /opt/training/audit-policy.yaml' < "$lab_directory/bootstrap/audit-policy.yaml"
# Widen the file permissions on purpose so that the benchmark file checks fail.
podman exec "$node_name" sh -c 'chmod 644 /etc/kubernetes/manifests/kube-apiserver.yaml /etc/kubernetes/manifests/kube-controller-manager.yaml /etc/kubernetes/manifests/kube-scheduler.yaml'
