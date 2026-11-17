#!/usr/bin/env bash
set -euo pipefail
context="${ASTRONA_KUBE_CONTEXT:-kind-astro-ats-031-lab-020-03-01}"
if [[ "$(kubectl config current-context)" != "$context" ]]; then
  printf 'Refusing to operate on another Kubernetes context\n' >&2
  exit 1
fi
cluster="${ASTRONA_KIND_CLUSTER:-astro-ats-031-lab-020-03-01}"
engine="${ASTRONA_CONTAINER_ENGINE:-podman}"
lab_directory="$(cd "$(dirname "$0")/.." && pwd)"
node_name="$cluster-control-plane"
worker_name="$cluster-worker"
namespace="starfleet-031-020-03-01"
source "$lab_directory/bootstrap/helpers.sh"
if [[ "$("$engine" inspect "$node_name" --format '{{index .Config.Labels "io.x-k8s.kind.cluster"}}')" != "$cluster" ]]; then
  printf 'Refusing to operate on an unrelated node container\n' >&2
  exit 1
fi
solution_directory="$lab_directory/solution"
run_on_node mkdir -p /etc/kubernetes/policy /var/log/kubernetes/audit
run_on_node cp /opt/training/audit-policy.yaml /etc/kubernetes/policy/audit-policy.yaml
edit_manifest kube-apiserver 's|^\( *\)- kube-apiserver$|&\n\1- --audit-policy-file=/etc/kubernetes/policy/audit-policy.yaml\n\1- --audit-log-path=/var/log/kubernetes/audit/audit.log\n\1- --audit-log-maxage=30\n\1- --audit-log-maxbackup=10\n\1- --audit-log-maxsize=100|
/^    volumeMounts:$/a\    - mountPath: /etc/kubernetes/policy\n      name: audit-policy\n      readOnly: true\n    - mountPath: /var/log/kubernetes/audit\n      name: audit-log
/^  volumes:$/a\  - hostPath:\n      path: /etc/kubernetes/policy\n      type: DirectoryOrCreate\n    name: audit-policy\n  - hostPath:\n      path: /var/log/kubernetes/audit\n      type: DirectoryOrCreate\n    name: audit-log'
wait_for_argument "$node_name" kube-apiserver --audit-log-path=/var/log/kubernetes/audit/audit.log present
wait_for_api
