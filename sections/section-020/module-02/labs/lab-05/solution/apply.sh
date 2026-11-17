#!/usr/bin/env bash
set -euo pipefail
context="${ASTRONA_KUBE_CONTEXT:-kind-astro-ats-031-lab-020-02-05}"
if [[ "$(kubectl config current-context)" != "$context" ]]; then
  printf 'Refusing to operate on another Kubernetes context\n' >&2
  exit 1
fi
cluster="${ASTRONA_KIND_CLUSTER:-astro-ats-031-lab-020-02-05}"
engine="${ASTRONA_CONTAINER_ENGINE:-podman}"
lab_directory="$(cd "$(dirname "$0")/.." && pwd)"
node_name="$cluster-control-plane"
worker_name="$cluster-worker"
namespace="starfleet-031-020-02-05"
source "$lab_directory/bootstrap/helpers.sh"
if [[ "$("$engine" inspect "$node_name" --format '{{index .Config.Labels "io.x-k8s.kind.cluster"}}')" != "$cluster" ]]; then
  printf 'Refusing to operate on an unrelated node container\n' >&2
  exit 1
fi
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
