#!/usr/bin/env bash
set -euo pipefail
context="${ASTRONA_KUBE_CONTEXT:-kubernetes-admin@astro-ats-031-lab-020-01-04}"
if [[ "$(kubectl config current-context)" != "$context" ]]; then
  printf 'Refusing to operate on another Kubernetes context\n' >&2
  exit 1
fi
cluster="astro-ats-031-lab-020-01-04"
lab_directory="$(cd "$(dirname "$0")/.." && pwd)"
# The VM is the only node: control plane and worker. kubeadm names it after
# the host name, which differs under `astrona test`.
node_name="$(hostname)"
worker_name="$node_name"
namespace="starfleet-031-020-01-04"
source "$lab_directory/bootstrap/helpers.sh"
solution_directory="$lab_directory/solution"
configuration="$(kubectl get --raw "/api/v1/nodes/$worker_name/proxy/configz")"
anonymous="$(python3 -c 'import json,sys; print(str(json.load(sys.stdin)["kubeletconfig"]["authentication"]["anonymous"]["enabled"]).lower())' <<<"$configuration")"
mode="$(python3 -c 'import json,sys; print(json.load(sys.stdin)["kubeletconfig"]["authorization"]["mode"])' <<<"$configuration")"
port="$(python3 -c 'import json,sys; print(json.load(sys.stdin)["kubeletconfig"].get("readOnlyPort", 0))' <<<"$configuration")"
kubectl -n "$namespace" create configmap kubelet-review \
  --from-literal=anonymous-enabled="$anonymous" \
  --from-literal=authorization-mode="$mode" \
  --from-literal=read-only-port="$port" \
  --dry-run=client -o yaml | kubectl apply -f -
run_on_worker chmod 600 /var/lib/kubelet/config.yaml
