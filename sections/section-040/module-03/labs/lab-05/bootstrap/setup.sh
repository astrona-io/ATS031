#!/usr/bin/env bash
# Removes NodeRestriction from the API server, then uses the worker kubelet's
# own credential to give the worker a protected label, as a stolen node
# credential could.
set -euo pipefail
context="${ASTRONA_KUBE_CONTEXT:-kind-astro-ats-031-lab-040-03-05}"
if [[ "$(kubectl config current-context)" != "$context" ]]; then
  printf 'Refusing to operate on another Kubernetes context\n' >&2
  exit 1
fi
cluster="${ASTRONA_KIND_CLUSTER:-astro-ats-031-lab-040-03-05}"
engine="${ASTRONA_CONTAINER_ENGINE:-podman}"
lab_directory="$(cd "$(dirname "$0")/.." && pwd)"
node_name="$cluster-control-plane"
worker_name="$cluster-worker"
manifest=/etc/kubernetes/manifests/kube-apiserver.yaml

kubectl apply -f "$lab_directory/bootstrap/manifests/namespace.yaml"

# Edit a copy outside the manifests directory, then move it back.
"$engine" exec "$node_name" sh -c "mkdir -p /etc/kubernetes/edit && cp -p $manifest /etc/kubernetes/edit/kube-apiserver.yaml && sed -i '/^ *- --enable-admission-plugins=NodeRestriction\$/d' /etc/kubernetes/edit/kube-apiserver.yaml && mv /etc/kubernetes/edit/kube-apiserver.yaml $manifest"

# The restarted API server accepts a server-side dry run of a write to
# another node from the worker credential once NodeRestriction is off.
as_worker() {
  "$engine" exec "$worker_name" kubectl --kubeconfig /etc/kubernetes/kubelet.conf --request-timeout=5s "$@"
}
for attempt in $(seq 1 80); do
  if output="$(as_worker label node "$node_name" lab-check=open --overwrite --dry-run=server 2>&1)"; then
    break
  fi
  if [[ "$attempt" == 80 ]]; then
    printf 'Timed out waiting for the API server without NodeRestriction. Last answer:\n%s\n' "$output" >&2
    "$engine" exec "$worker_name" sh -c 'command -v kubectl; ls -l /etc/kubernetes' >&2 || true
    "$engine" exec "$node_name" grep -nE 'authorization-mode|admission-plugins' "$manifest" >&2 || true
    exit 1
  fi
  sleep 3
done
# The kubelet updates the mirror pod of the static pod a moment later.
for attempt in $(seq 1 40); do
  if ! kubectl -n kube-system get pod "kube-apiserver-$node_name" -o jsonpath='{.spec.containers[0].command}' 2>/dev/null | grep -q NodeRestriction; then
    break
  fi
  sleep 3
done
as_worker label node "$worker_name" node-restriction.kubernetes.io/dedicated=payments --overwrite
kubectl wait --for=condition=Ready "node/$worker_name" --timeout=180s
