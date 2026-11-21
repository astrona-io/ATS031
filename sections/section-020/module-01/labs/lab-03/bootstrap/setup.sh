#!/usr/bin/env bash
# Runs inside the lab VM from /opt/astrona-lab after vm/install.sh built the cluster.
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
kubectl apply -f "$lab_directory/bootstrap/manifests/start.yaml"
kubectl -n starfleet-031-020-01-03 rollout status deployment/probe --timeout=180s
kubectl -n starfleet-031-020-01-03 wait --for=condition=Ready pod/shuttle --timeout=120s
kubectl -n outpost-031-020-01-03 wait --for=condition=Ready pod/drifter --timeout=120s
profiling_choices=(true false)
mode_choices=(700 750 755)
profiling="${profiling_choices[RANDOM % 2]}"
data_mode="${mode_choices[RANDOM % 3]}"
run_on_node chmod "$data_mode" /var/lib/etcd
if [[ "$profiling" == false ]]; then
  edit_manifest kube-apiserver 's|^\( *\)- kube-apiserver$|&\n\1- --profiling=false|'
  wait_for_argument "$node_name" kube-apiserver --profiling=false present
  wait_for_api
fi
# The grader compares the running cluster with the settings chosen here.
run_on_node mkdir -p /var/lib/astrona-lab
printf 'profiling=%s\ndata_mode=%s\n' "$profiling" "$data_mode" | run_on_node tee /var/lib/astrona-lab/020-01-03-staged >/dev/null
run_on_node chmod 0600 /var/lib/astrona-lab/020-01-03-staged
