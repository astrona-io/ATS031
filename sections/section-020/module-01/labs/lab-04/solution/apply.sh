#!/usr/bin/env bash
set -euo pipefail
context="${ASTRONA_KUBE_CONTEXT:-kind-astro-ats-031-lab-020-01-04}"
if [[ "$(kubectl config current-context)" != "$context" ]]; then
  printf 'Refusing to operate on another Kubernetes context\n' >&2
  exit 1
fi
cluster="${ASTRONA_KIND_CLUSTER:-astro-ats-031-lab-020-01-04}"
engine="${ASTRONA_CONTAINER_ENGINE:-podman}"
lab_directory="$(cd "$(dirname "$0")/.." && pwd)"
node_name="$cluster-control-plane"
worker_name="$cluster-worker"
namespace="starfleet-031-020-01-04"
source "$lab_directory/bootstrap/helpers.sh"
if [[ "$("$engine" inspect "$node_name" --format '{{index .Config.Labels "io.x-k8s.kind.cluster"}}')" != "$cluster" ]]; then
  printf 'Refusing to operate on an unrelated node container\n' >&2
  exit 1
fi
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
