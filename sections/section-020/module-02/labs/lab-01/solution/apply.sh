#!/usr/bin/env bash
set -euo pipefail
context="${ASTRONA_KUBE_CONTEXT:-kind-astro-ats-031-lab-020-02-01}"
if [[ "$(kubectl config current-context)" != "$context" ]]; then
  printf 'Refusing to operate on another Kubernetes context\n' >&2
  exit 1
fi
cluster="${ASTRONA_KIND_CLUSTER:-astro-ats-031-lab-020-02-01}"
lab_directory="$(cd "$(dirname "$0")/.." && pwd)"
solution_directory="$lab_directory/solution"
node_name="$cluster-control-plane"
work_file="$(mktemp)"
kubectl apply -f "$solution_directory/job-kube-bench-master.yaml"
kubectl -n default wait --for=condition=complete job/kube-bench-master --timeout=180s
kubectl -n default logs job/kube-bench-master | grep -E '^\[FAIL\] 1\.2\.' | awk '{print $2}' | sort -V > "$work_file"
kubectl -n starfleet-031-020-02-01 create configmap failing-checks --from-file=ids="$work_file" --dry-run=client -o yaml | kubectl apply -f -
rm -f "$work_file"
