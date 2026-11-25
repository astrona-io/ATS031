#!/usr/bin/env bash
set -euo pipefail
context="${ASTRONA_KUBE_CONTEXT:-kubernetes-admin@astro-ats-031-lab-020-04-01}"
if [[ "$(kubectl config current-context)" != "$context" ]]; then
  printf 'Refusing to operate on another Kubernetes context\n' >&2
  exit 1
fi
cluster="astro-ats-031-lab-020-04-01"
lab_directory="$(cd "$(dirname "$0")/.." && pwd)"
# The VM is the only node: control plane and worker. kubeadm names it after
# the host name, which differs under `astrona test`.
node_name="$(hostname)"
worker_name="$node_name"
namespace="starfleet-031-020-04-01"
source "$lab_directory/bootstrap/helpers.sh"
solution_directory="$lab_directory/solution"
key="$(head -c 32 /dev/urandom | base64)"
run_on_node mkdir -p /etc/kubernetes/enc
sed "s|<KEY>|$key|" "$solution_directory/encryption-config.yaml" | sudo sh -c 'cat > /etc/kubernetes/enc/encryption-config.yaml'
run_on_node chmod 600 /etc/kubernetes/enc/encryption-config.yaml
edit_manifest kube-apiserver 's|^\( *\)- kube-apiserver$|&\n\1- --encryption-provider-config=/etc/kubernetes/enc/encryption-config.yaml|
/^    volumeMounts:$/a\    - mountPath: /etc/kubernetes/enc\n      name: enc\n      readOnly: true
/^  volumes:$/a\  - hostPath:\n      path: /etc/kubernetes/enc\n      type: DirectoryOrCreate\n    name: enc'
wait_for_argument "$node_name" kube-apiserver --encryption-provider-config=/etc/kubernetes/enc/encryption-config.yaml present
wait_for_api
for attempt in $(seq 1 5); do
  if kubectl get secrets --all-namespaces -o json | kubectl replace -f - >/dev/null; then
    break
  fi
  sleep 3
done
