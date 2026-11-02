#!/usr/bin/env bash
set -euo pipefail
if [[ "$(kubectl config current-context)" != "kind-astro-ats-031-lab-010-01-02" ]]; then
  printf 'Refusing to operate on another Kubernetes context\n' >&2
  exit 1
fi
lab_directory="$(cd "$(dirname "$0")/.." && pwd)"
solution_directory="$lab_directory/solution"
cluster_name="astro-ats-031-lab-010-01-02"

kubectl apply -f "$solution_directory/pod-blocked-server.yaml"
kubectl -n starfleet wait --for=condition=Ready pod/blocked-server --timeout=180s
