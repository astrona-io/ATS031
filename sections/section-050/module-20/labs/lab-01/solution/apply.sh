#!/usr/bin/env bash
# Reference solution: read the stable version and the worker architecture,
# build the release path of kubeadm and record it with its published digest.
set -euo pipefail
context="${ASTRONA_KUBE_CONTEXT:-kind-astro-ats-031-lab-050-02-01}"
if [[ "$(kubectl config current-context)" != "$context" ]]; then
  printf 'Refusing to operate on another Kubernetes context\n' >&2
  exit 1
fi
cluster="${ASTRONA_KIND_CLUSTER:-astro-ats-031-lab-050-02-01}"
engine="${ASTRONA_CONTAINER_ENGINE:-podman}"
node_name="$cluster-control-plane"
stable_version=$("$engine" exec "$node_name" cat /var/lib/k8s-mirror/release/stable.txt)
worker_architecture=$(kubectl get node "$cluster-worker" -o jsonpath='{.status.nodeInfo.architecture}')
release_path="release/$stable_version/bin/linux/$worker_architecture/kubeadm"
published_digest=$("$engine" exec "$node_name" cat "/var/lib/k8s-mirror/$release_path.sha256")
kubectl -n starfleet-031-050-02-01 create configmap release-pick \
  --from-literal=path="$release_path" --from-literal=sha256="$published_digest" \
  --dry-run=client -o yaml | kubectl apply -f -
