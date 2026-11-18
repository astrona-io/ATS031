#!/usr/bin/env bash
set -euo pipefail
context="${ASTRONA_KUBE_CONTEXT:-kubernetes-admin@astro-ats-031-lab-020-01-03}"
if [[ "$(kubectl config current-context)" != "$context" ]]; then
  printf 'Refusing to operate on another Kubernetes context\n' >&2
  exit 1
fi
cluster="astro-ats-031-lab-020-01-03"
lab_directory="$(cd "$(dirname "$0")/.." && pwd)"
# The VM is the only node: control plane and worker. kubeadm names it after
# the host name, which differs under `astrona test`.
node_name="$(hostname)"
worker_name="$node_name"
namespace="starfleet-031-020-01-03"
source "$lab_directory/bootstrap/helpers.sh"
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
