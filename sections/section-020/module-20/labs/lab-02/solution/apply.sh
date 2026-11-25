#!/usr/bin/env bash
set -euo pipefail
context="${ASTRONA_KUBE_CONTEXT:-kubernetes-admin@astro-ats-031-lab-020-02-02}"
if [[ "$(kubectl config current-context)" != "$context" ]]; then
  printf 'Refusing to operate on another Kubernetes context\n' >&2
  exit 1
fi
cluster="astro-ats-031-lab-020-02-02"
lab_directory="$(cd "$(dirname "$0")/.." && pwd)"
# The VM is the only node: control plane and worker. kubeadm names it after
# the host name, which differs under `astrona test`.
node_name="$(hostname)"
worker_name="$node_name"
namespace="starfleet-031-020-02-02"
source "$lab_directory/bootstrap/helpers.sh"
solution_directory="$lab_directory/solution"
edition="$(kubectl -n "$namespace" get configmap audit-request -o jsonpath='{.data.edition}')"
files="$(kube_bench_image_output kube-bench-files "ls /opt/kube-bench/cfg/$edition")"
check="$(kube_bench_image_output kube-bench-master "cat /opt/kube-bench/cfg/$edition/master.yaml" | awk '/^ *- id: 1\.2\./ {id=$3} /^ *text:/ && /--profiling/ && id {print id; exit}')"
test -n "$check"
kubectl -n "$namespace" create configmap check-definition --from-literal=files="$files" --from-literal=apiserver-profiling-check="$check" --dry-run=client -o yaml | kubectl apply -f -
