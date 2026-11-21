#!/usr/bin/env bash
# Runs inside the lab VM from /opt/astrona-lab after vm/install.sh built the cluster.
set -euo pipefail
context="${ASTRONA_KUBE_CONTEXT:-kubernetes-admin@astro-ats-031-lab-020-02-01}"
if [[ "$(kubectl config current-context)" != "$context" ]]; then
  printf 'Refusing to operate on another Kubernetes context\n' >&2
  exit 1
fi
cluster="astro-ats-031-lab-020-02-01"
lab_directory="$(cd "$(dirname "$0")/.." && pwd)"
# The VM is the only node: control plane and worker. kubeadm names it after
# the host name, which differs under `astrona test`.
node_name="$(hostname)"
worker_name="$node_name"
namespace="starfleet-031-020-02-01"
source "$lab_directory/bootstrap/helpers.sh"
kubectl apply -f "$lab_directory/bootstrap/manifests/start.yaml"
kubectl -n starfleet-031-020-02-01 rollout status deployment/probe --timeout=180s
kubectl -n starfleet-031-020-02-01 wait --for=condition=Ready pod/shuttle --timeout=120s
kubectl -n outpost-031-020-02-01 wait --for=condition=Ready pod/drifter --timeout=120s
# The grader compares the cluster settings with this list of digests.
run_on_node mkdir -p /var/lib/astrona-lab
run_on_node sh -c 'sha256sum /etc/kubernetes/manifests/*.yaml /var/lib/kubelet/config.yaml > /var/lib/astrona-lab/020-02-01-staged'
run_on_node chmod 0600 /var/lib/astrona-lab/020-02-01-staged
