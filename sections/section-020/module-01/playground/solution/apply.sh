#!/usr/bin/env bash
set -euo pipefail
if [[ "$(kubectl config current-context)" != "kind-astro-ats-031-playground-020-01" ]]; then
  printf 'Refusing to operate on another Kubernetes context\n' >&2
  exit 1
fi
lab_directory="$(cd "$(dirname "$0")/.." && pwd)"
solution_directory="$lab_directory/solution"
node_name="astro-ats-031-playground-020-01-control-plane"
worker_name="astro-ats-031-playground-020-01-worker"
python3 "$solution_directory/configure-api.py"
api_ready=0
for attempt in $(seq 1 80); do
  if kubectl --request-timeout=3s get --raw=/readyz >/dev/null 2>&1; then api_ready=1; break; fi
  sleep 3
done
test "$api_ready" -eq 1

kubectl apply -f "$solution_directory/configmap-benchmark-review.yaml"
