#!/usr/bin/env bash
set -euo pipefail
context="${ASTRONA_KUBE_CONTEXT:-kind-astro-ats-031-lab-020-03-01}"
if [[ "$(kubectl config current-context)" != "$context" ]]; then
  printf 'Refusing to operate on another Kubernetes context\n' >&2
  exit 1
fi
cluster="${ASTRONA_KIND_CLUSTER:-astro-ats-031-lab-020-03-01}"
engine="${ASTRONA_CONTAINER_ENGINE:-podman}"
lab_directory="$(cd "$(dirname "$0")/.." && pwd)"
node_name="$cluster-control-plane"
worker_name="$cluster-worker"
kubectl apply -f "$lab_directory/bootstrap/manifests/start.yaml"
kubectl -n starfleet-031-020-03-01 rollout status deployment/probe --timeout=180s
kubectl -n starfleet-031-020-03-01 wait --for=condition=Ready pod/shuttle --timeout=120s
kubectl -n outpost-031-020-03-01 wait --for=condition=Ready pod/drifter --timeout=120s
if [[ "$("$engine" inspect "$node_name" --format '{{index .Config.Labels "io.x-k8s.kind.cluster"}}')" != "$cluster" ]]; then
  printf 'Refusing to operate on an unrelated node container\n' >&2
  exit 1
fi
# Working copies of the original manifests, kept outside the manifests directory.
"$engine" exec "$node_name" mkdir -p /opt/training/backup
"$engine" exec "$node_name" sh -c 'cp -p /etc/kubernetes/manifests/*.yaml /opt/training/backup/'
# Stage an audit policy that no component references yet.
"$engine" exec -i "$node_name" sh -c 'cat > /opt/training/audit-policy.yaml' < "$lab_directory/bootstrap/audit-policy.yaml"
# Widen the file permissions on purpose so that the benchmark file checks fail.
"$engine" exec "$node_name" sh -c 'chmod 644 /etc/kubernetes/manifests/kube-apiserver.yaml /etc/kubernetes/manifests/kube-controller-manager.yaml /etc/kubernetes/manifests/kube-scheduler.yaml'
