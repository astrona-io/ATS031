#!/usr/bin/env bash
set -euo pipefail
context="${ASTRONA_KUBE_CONTEXT:-kind-astro-ats-031-lab-040-03-02}"
if [[ "$(kubectl config current-context)" != "$context" ]]; then
  printf 'Refusing to operate on another Kubernetes context\n' >&2
  exit 1
fi
printf 'dock-031-040-03-02/net-tool\noutpost-031-040-03-02/runtime-peek\nstarfleet-031-040-03-02/cri-helper\n' > /tmp/exposed-pods.txt
kubectl -n dock-031-040-03-02 create configmap exposed-pods --from-file=pods=/tmp/exposed-pods.txt --dry-run=client -o yaml | kubectl apply -f -
