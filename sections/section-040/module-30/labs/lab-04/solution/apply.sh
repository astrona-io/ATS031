#!/usr/bin/env bash
set -euo pipefail
context="${ASTRONA_KUBE_CONTEXT:-kind-astro-ats-031-lab-040-03-04}"
if [[ "$(kubectl config current-context)" != "$context" ]]; then
  printf 'Refusing to operate on another Kubernetes context\n' >&2
  exit 1
fi
host_network_pods="$(kubectl get pods -n dock-031-040-03-04 -o jsonpath='{range .items[?(@.spec.hostNetwork==true)]}{.metadata.namespace}{"/"}{.metadata.name}{"\n"}{end}')
$(kubectl get pods -n outpost-031-040-03-04 -o jsonpath='{range .items[?(@.spec.hostNetwork==true)]}{.metadata.namespace}{"/"}{.metadata.name}{"\n"}{end}')"
kubectl -n dock-031-040-03-04 create configmap host-network-pods --from-literal=pods="$host_network_pods" --dry-run=client -o yaml | kubectl apply -f -
kubectl label --overwrite namespace dock-031-040-03-04 pod-security.kubernetes.io/enforce=baseline
