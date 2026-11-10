#!/usr/bin/env bash
set -euo pipefail
context="${ASTRONA_KUBE_CONTEXT:-kind-astro-ats-031-capstone-010}"
if [[ "$(kubectl config current-context)" != "$context" ]]; then
  printf 'Refusing to operate on another Kubernetes context\n' >&2
  exit 1
fi
lab_directory="$(cd "$(dirname "$0")/.." && pwd)"
solution_directory="$lab_directory/solution"
kubectl apply -f "$solution_directory/networkpolicy-default-deny-all-starfleet.yaml"
kubectl apply -f "$solution_directory/networkpolicy-default-deny-all-outpost.yaml"
kubectl apply -f "$solution_directory/networkpolicy-default-deny-all-dock.yaml"
kubectl apply -f "$solution_directory/networkpolicy-probe-from-outpost.yaml"
kubectl apply -f "$solution_directory/networkpolicy-shuttle-egress.yaml"
api_address="$(kubectl get endpointslice -l kubernetes.io/service-name=kubernetes -o jsonpath='{.items[0].endpoints[0].addresses[0]}')"
api_port="$(kubectl get endpointslice -l kubernetes.io/service-name=kubernetes -o jsonpath='{.items[0].ports[0].port}')"
rendered="$(mktemp)"
sed -e "s/<API_ADDRESS>/${api_address}/" -e "s/<API_PORT>/${api_port}/" "$solution_directory/networkpolicy-scout-egress.yaml.template" > "$rendered"
kubectl apply -f "$rendered"
rm -f "$rendered"
