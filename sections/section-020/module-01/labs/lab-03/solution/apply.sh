#!/usr/bin/env bash
set -euo pipefail
context="${ASTRONA_KUBE_CONTEXT:-kind-astro-ats-031-lab-020-01-03}"
if [[ "$(kubectl config current-context)" != "$context" ]]; then
  printf 'Refusing to operate on another Kubernetes context\n' >&2
  exit 1
fi
cluster="${ASTRONA_KIND_CLUSTER:-astro-ats-031-lab-020-01-03}"
engine="${ASTRONA_CONTAINER_ENGINE:-podman}"
lab_directory="$(cd "$(dirname "$0")/.." && pwd)"
node_name="$cluster-control-plane"
worker_name="$cluster-worker"
namespace="starfleet-031-020-01-03"
source "$lab_directory/bootstrap/helpers.sh"
if [[ "$("$engine" inspect "$node_name" --format '{{index .Config.Labels "io.x-k8s.kind.cluster"}}')" != "$cluster" ]]; then
  printf 'Refusing to operate on an unrelated node container\n' >&2
  exit 1
fi
solution_directory="$lab_directory/solution"
arguments="$(process_arguments "$node_name" kube-apiserver)"
authorization_mode="$({ grep '^--authorization-mode=' <<<"$arguments" || true; } | tail -n 1 | cut -d= -f2)"
profiling="$({ grep '^--profiling=' <<<"$arguments" || true; } | tail -n 1 | cut -d= -f2)"
etcd_arguments="$(process_arguments "$node_name" etcd)"
client_cert_auth="$({ grep '^--client-cert-auth=' <<<"$etcd_arguments" || true; } | tail -n 1 | cut -d= -f2)"
data_mode="$(run_on_node stat -c %a /var/lib/etcd)"
kubectl -n "$namespace" create configmap manual-audit \
  --from-literal=apiserver-authorization-mode="$authorization_mode" \
  --from-literal=apiserver-profiling="${profiling:-true}" \
  --from-literal=etcd-client-cert-auth="${client_cert_auth:-false}" \
  --from-literal=etcd-data-dir-mode="$data_mode" \
  --dry-run=client -o yaml | kubectl apply -f -
