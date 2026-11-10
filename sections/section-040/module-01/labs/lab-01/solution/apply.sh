#!/usr/bin/env bash
set -euo pipefail
context="${ASTRONA_KUBE_CONTEXT:-kind-astro-ats-031-lab-040-01-01}"
if [[ "$(kubectl config current-context)" != "$context" ]]; then
  printf 'Refusing to operate on another Kubernetes context\n' >&2
  exit 1
fi
cluster="${ASTRONA_KIND_CLUSTER:-astro-ats-031-lab-040-01-01}"
lab_directory="$(cd "$(dirname "$0")/.." && pwd)"
solution_directory="$lab_directory/solution"
node_name="$cluster-control-plane"
worker_name="$cluster-worker"

kubectl apply -f "$solution_directory/pod-metadata-simulator.yaml"
kubectl -n starfleet-031-040-01-01 wait --for=condition=Ready pod/metadata-simulator --timeout=180s
