#!/usr/bin/env bash
set -euo pipefail
context="${ASTRONA_KUBE_CONTEXT:-kind-astro-ats-031-lab-020-04-01}"
if [[ "$(kubectl config current-context)" != "$context" ]]; then
  printf 'Refusing to operate on another Kubernetes context\n' >&2
  exit 1
fi
cluster="${ASTRONA_KIND_CLUSTER:-astro-ats-031-lab-020-04-01}"
lab_directory="$(cd "$(dirname "$0")/.." && pwd)"
solution_directory="$lab_directory/solution"
node_name="$cluster-control-plane"
worker_name="$cluster-worker"
python3 "$solution_directory/enable-encryption.py"
api_ready=0
for attempt in $(seq 1 80); do
  if kubectl --request-timeout=3s -n kube-system get pod "kube-apiserver-$node_name" -o jsonpath='{.spec.containers[0].command}' 2>/dev/null | grep -q -e 'encryption-provider-config' \
    && kubectl --request-timeout=3s get --raw=/readyz >/dev/null 2>&1; then api_ready=1; break; fi
  sleep 3
done
test "$api_ready" -eq 1
kubectl get secrets --all-namespaces -o json | kubectl replace -f -
