#!/usr/bin/env bash
set -euo pipefail
context="${ASTRONA_KUBE_CONTEXT:-kubernetes-admin@astro-ats-031-lab-020-03-02}"
if [[ "$(kubectl config current-context)" != "$context" ]]; then
  printf 'Refusing to operate on another Kubernetes context\n' >&2
  exit 1
fi
cluster="astro-ats-031-lab-020-03-02"
lab_directory="$(cd "$(dirname "$0")/.." && pwd)"
# The VM is the only node: control plane and worker.
node_name="$cluster"
worker_name="$cluster"
namespace="starfleet-031-020-03-02"
source "$lab_directory/bootstrap/helpers.sh"
solution_directory="$lab_directory/solution"
edit_manifest kube-apiserver 's|--tls-min-version=VersionTLS10|--tls-min-version=VersionTLS12|; s|^\( *\)- kube-apiserver$|&\n\1- --profiling=false|'
wait_for_argument "$node_name" kube-apiserver --profiling=false present
wait_for_api
