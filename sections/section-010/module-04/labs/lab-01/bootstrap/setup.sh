#!/usr/bin/env bash
set -euo pipefail
context="${ASTRONA_KUBE_CONTEXT:-kind-astro-ats-031-lab-010-04-01}"
if [[ "$(kubectl config current-context)" != "$context" ]]; then
  printf 'Refusing to operate on another Kubernetes context\n' >&2
  exit 1
fi
lab_directory="$(cd "$(dirname "$0")/.." && pwd)"
kubectl apply -f "$lab_directory/bootstrap/manifests/base.yaml"
kubectl -n starfleet-031-010-04-01 rollout status deployment/probe --timeout=180s
kubectl apply -f "$lab_directory/bootstrap/manifests/scout.yaml"
kubectl -n starfleet-031-010-04-01 wait --for=condition=Ready pod/scout --timeout=120s
kubectl -n starfleet-031-010-04-01 wait --for=condition=Ready pod/beacon --timeout=120s
kubectl -n outpost-031-010-04-01 wait --for=condition=Ready pod/drifter --timeout=120s
api_address="$(kubectl get endpointslice -l kubernetes.io/service-name=kubernetes -o jsonpath='{.items[0].endpoints[0].addresses[0]}')"
api_port="$(kubectl get endpointslice -l kubernetes.io/service-name=kubernetes -o jsonpath='{.items[0].ports[0].port}')"
rendered="$(mktemp)"
sed -e "s/__API_IP__/${api_address}/" -e "s/__API_PORT__/${api_port}/" "$lab_directory/bootstrap/manifests/policies.yaml.template" > "$rendered"
kubectl apply -f "$rendered"
rm -f "$rendered"
