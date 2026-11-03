#!/usr/bin/env bash
# Reference result, applied only by astrona test. Kept in step with solution.md.
set -euo pipefail
CONTROL="astro-ats-031-lab-050-02-01-control-plane"
WORKER="astro-ats-031-lab-050-02-01-worker"
if [[ "$(kubectl config current-context)" != "kind-astro-ats-031-lab-050-02-01" ]]; then
  printf "Refusing to operate on another Kubernetes context
" >&2
  exit 1
fi
R=/var/lib/training-release/k8s/lab
for tool in kubectl kubeadm kubelet; do
  expected="$(podman exec "$CONTROL" cat "$R/$tool.sha256")"
  actual="$(podman exec "$CONTROL" sha256sum "$R/$tool" | cut -d' ' -f1)"
  if [[ "$expected" != "$actual" ]]; then
    podman exec "$CONTROL" sh -c "printf '%s\n' $tool > $R/result.txt"
  fi
done
