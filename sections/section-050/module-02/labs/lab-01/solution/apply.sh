#!/usr/bin/env bash
# Reference result, applied only by astrona test. Kept in step with solution.md.
set -euo pipefail
context="${ASTRONA_KUBE_CONTEXT:-kind-astro-ats-031-lab-050-02-01}"
if [[ "$(kubectl config current-context)" != "$context" ]]; then
  printf 'Refusing to operate on another Kubernetes context\n' >&2
  exit 1
fi
cluster="${ASTRONA_KIND_CLUSTER:-astro-ats-031-lab-050-02-01}"
engine="${ASTRONA_CONTAINER_ENGINE:-podman}"
node_name="$cluster-control-plane"
R=/var/lib/training-release/k8s/lab
for tool in kubectl kubeadm kubelet; do
  expected="$("$engine" exec "$node_name" cat "$R/$tool.sha256")"
  actual="$("$engine" exec "$node_name" sha256sum "$R/$tool" | cut -d' ' -f1)"
  if [[ "$expected" != "$actual" ]]; then
    "$engine" exec "$node_name" sh -c "printf '%s\n' $tool > $R/result.txt"
  fi
done
