#!/usr/bin/env bash
set -euo pipefail
context="${ASTRONA_KUBE_CONTEXT:-kind-astro-ats-031-lab-040-03-05}"
if [[ "$(kubectl config current-context)" != "$context" ]]; then
  printf 'Refusing to operate on another Kubernetes context\n' >&2
  exit 1
fi
cluster="${ASTRONA_KIND_CLUSTER:-astro-ats-031-lab-040-03-05}"
engine="${ASTRONA_CONTAINER_ENGINE:-podman}"
node_name="$cluster-control-plane"
worker_name="$cluster-worker"
manifest=/etc/kubernetes/manifests/kube-apiserver.yaml

"$engine" exec "$node_name" sh -c "mkdir -p /etc/kubernetes/edit && cp -p $manifest /etc/kubernetes/edit/kube-apiserver.yaml && sed -i 's|^\( *\)- --authorization-mode=Node,RBAC\$|&\n\1- --enable-admission-plugins=NodeRestriction|' /etc/kubernetes/edit/kube-apiserver.yaml && mv /etc/kubernetes/edit/kube-apiserver.yaml $manifest"

# Wait until the restarted API server refuses the same write as forbidden.
for attempt in $(seq 1 80); do
  output="$("$engine" exec "$worker_name" kubectl --kubeconfig /etc/kubernetes/kubelet.conf --request-timeout=5s label node "$node_name" lab-check=open --overwrite --dry-run=server 2>&1 || true)"
  if grep -qi forbidden <<<"$output"; then
    break
  fi
  if [[ "$attempt" == 80 ]]; then
    printf 'Timed out waiting for the API server with NodeRestriction\n' >&2
    exit 1
  fi
  sleep 3
done
kubectl label node "$worker_name" node-restriction.kubernetes.io/dedicated-
