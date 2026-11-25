#!/usr/bin/env bash
# Reference solution: find the binary of the running kubelet process on the
# worker, compute its digest, compare it with the published v1.35.0 digest for
# the worker architecture and record the result.
set -euo pipefail
context="${ASTRONA_KUBE_CONTEXT:-kind-astro-ats-031-lab-050-02-05}"
if [[ "$(kubectl config current-context)" != "$context" ]]; then
  printf 'Refusing to operate on another Kubernetes context\n' >&2
  exit 1
fi
cluster="${ASTRONA_KIND_CLUSTER:-astro-ats-031-lab-050-02-05}"
engine="${ASTRONA_CONTAINER_ENGINE:-podman}"
worker_name="$cluster-worker"
kubelet_pid=$("$engine" exec "$worker_name" pidof kubelet)
running_path=$("$engine" exec "$worker_name" readlink "/proc/$kubelet_pid/exe")
running_digest=$("$engine" exec "$worker_name" sha256sum "/proc/$kubelet_pid/exe" | cut -d' ' -f1)
kubelet_version=$(kubectl get node "$worker_name" -o jsonpath='{.status.nodeInfo.kubeletVersion}')
worker_architecture=$(kubectl get node "$worker_name" -o jsonpath='{.status.nodeInfo.architecture}')
published_digest=$("$engine" exec "$worker_name" cat "/var/lib/kubelet-release/$kubelet_version/bin/linux/$worker_architecture/kubelet.sha256")
if [[ "$running_digest" == "$published_digest" ]]; then checksum_result=match; else checksum_result=mismatch; fi
kubectl -n starfleet-031-050-02-05 create configmap kubelet-review \
  --from-literal=version="$kubelet_version" --from-literal=path="$running_path" \
  --from-literal=sha256="$running_digest" --from-literal=result="$checksum_result" \
  --dry-run=client -o yaml | kubectl apply -f -
