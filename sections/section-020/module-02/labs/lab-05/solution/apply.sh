#!/usr/bin/env bash
set -euo pipefail
context="${ASTRONA_KUBE_CONTEXT:-kubernetes-admin@astro-ats-031-lab-020-02-05}"
if [[ "$(kubectl config current-context)" != "$context" ]]; then
  printf 'Refusing to operate on another Kubernetes context\n' >&2
  exit 1
fi
cluster="astro-ats-031-lab-020-02-05"
lab_directory="$(cd "$(dirname "$0")/.." && pwd)"
# The VM is the only node: control plane and worker. kubeadm names it after
# the host name, which differs under `astrona test`.
node_name="$(hostname)"
worker_name="$node_name"
namespace="starfleet-031-020-02-05"
source "$lab_directory/bootstrap/helpers.sh"
solution_directory="$lab_directory/solution"
kubectl apply -f "$solution_directory/job-master-audit.yaml"
kubectl -n "$namespace" wait --for=condition=complete job/master-audit --timeout=180s
log="$(kubectl -n "$namespace" logs job/master-audit)"
total() { grep -E "^[0-9]+ checks $1\$" <<<"$log" | tail -n 1 | cut -d' ' -f1; }
count() { grep -cE "^\[FAIL\] $1\." <<<"$log" || true; }
kubectl -n "$namespace" create configmap master-result \
  --from-literal=pass="$(total PASS)" --from-literal=fail="$(total FAIL)" \
  --from-literal=warn="$(total WARN)" --from-literal=info="$(total INFO)" \
  --from-literal=fail-1.1="$(count '1\.1')" --from-literal=fail-1.2="$(count '1\.2')" \
  --dry-run=client -o yaml | kubectl apply -f -
