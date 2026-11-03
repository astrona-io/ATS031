#!/usr/bin/env bash
set -euo pipefail
if [[ "$(kubectl config current-context)" != "kind-astro-ats-031-lab-010-04-01" ]]; then
  printf 'Refusing to operate on another Kubernetes context\n' >&2
  exit 1
fi
lab_directory="$(cd "$(dirname "$0")/.." && pwd)"
solution_directory="$lab_directory/solution"
kubectl apply -f "$solution_directory/networkpolicy-scout-dns.yaml"
kubectl apply -f "$solution_directory/networkpolicy-scout-to-probe.yaml"
kubectl apply -f "$solution_directory/networkpolicy-probe-ingress.yaml"
