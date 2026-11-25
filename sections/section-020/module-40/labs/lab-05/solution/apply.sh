#!/usr/bin/env bash
set -euo pipefail
context="${ASTRONA_KUBE_CONTEXT:-kubernetes-admin@astro-ats-031-lab-020-04-05}"
if [[ "$(kubectl config current-context)" != "$context" ]]; then
  printf 'Refusing to operate on another Kubernetes context\n' >&2
  exit 1
fi
cluster="astro-ats-031-lab-020-04-05"
lab_directory="$(cd "$(dirname "$0")/.." && pwd)"
# The VM is the only node: control plane and worker. kubeadm names it after
# the host name, which differs under `astrona test`.
node_name="$(hostname)"
worker_name="$node_name"
namespace="starfleet-031-020-04-05"
source "$lab_directory/bootstrap/helpers.sh"
solution_directory="$lab_directory/solution"
key="$(kubectl -n kube-system exec "etcd-$node_name" -- etcdctl --endpoints=https://127.0.0.1:2379 --cacert=/etc/kubernetes/pki/etcd/ca.crt --cert=/etc/kubernetes/pki/etcd/healthcheck-client.crt --key=/etc/kubernetes/pki/etcd/healthcheck-client.key get /registry/secrets/ --prefix --keys-only | grep '/relay-token$' | head -n 1)"
test -n "$key"
member="$(kubectl -n kube-system exec "etcd-$node_name" -- etcdctl --endpoints=https://127.0.0.1:2379 --cacert=/etc/kubernetes/pki/etcd/ca.crt --cert=/etc/kubernetes/pki/etcd/healthcheck-client.crt --key=/etc/kubernetes/pki/etcd/healthcheck-client.key member list -w simple | cut -d, -f3 | tr -d ' ' | head -n 1)"
kubectl -n "$namespace" create configmap etcd-query --from-literal=secret-key="$key" --from-literal=secret-namespace="$(cut -d/ -f4 <<<"$key")" --from-literal=member-name="$member" --dry-run=client -o yaml | kubectl apply -f -
