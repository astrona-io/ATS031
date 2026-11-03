#!/usr/bin/env bash
set -euo pipefail
if [[ "$(kubectl config current-context)" != "kind-astro-ats-031-lab-020-02-01" ]]; then
  printf 'Refusing to operate on another Kubernetes context\n' >&2
  exit 1
fi
lab_directory="$(cd "$(dirname "$0")/.." && pwd)"
solution_directory="$lab_directory/solution"
node_name="astro-ats-031-lab-020-02-01-control-plane"
work_file="$(mktemp)"
kubectl apply -f "$solution_directory/job-kube-bench-master.yaml"
kubectl -n default wait --for=condition=complete job/kube-bench-master --timeout=180s
kubectl -n default logs job/kube-bench-master | grep -E '^\[FAIL\] 1\.2\.' | awk '{print $2}' | sort -V > "$work_file"
kubectl -n starfleet create configmap failing-checks --from-file=ids="$work_file" --dry-run=client -o yaml | kubectl apply -f -
rm -f "$work_file"
