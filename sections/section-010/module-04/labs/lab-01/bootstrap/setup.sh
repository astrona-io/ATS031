#!/usr/bin/env bash
set -euo pipefail
context="${ASTRONA_KUBE_CONTEXT:-kind-astro-ats-031-lab-010-04-01}"
if [[ "$(kubectl config current-context)" != "$context" ]]; then
  printf 'Refusing to operate on another Kubernetes context\n' >&2
  exit 1
fi
lab_directory="$(cd "$(dirname "$0")/.." && pwd)"
kubectl apply -f "$lab_directory/bootstrap/manifests/start.yaml"
kubectl -n starfleet-031-010-04-01 wait --for=condition=Ready pod/pathfinder --timeout=180s
kubectl -n starfleet-031-010-04-01 wait --for=condition=Ready pod/datastore --timeout=180s
kubectl -n starfleet-031-010-04-01 wait --for=condition=Ready pod/stranger --timeout=180s
api_ip="$(kubectl get endpointslice -n default -l kubernetes.io/service-name=kubernetes -o jsonpath='{.items[0].endpoints[0].addresses[0]}')"
api_port="$(kubectl get endpointslice -n default -l kubernetes.io/service-name=kubernetes -o jsonpath='{.items[0].ports[0].port}')"
sed -e "s|<API_SERVER_IP>|$api_ip|" -e "s|<API_SERVER_PORT>|$api_port|" "$lab_directory/bootstrap/manifests/networkpolicy-pathfinder-egress.yaml" | kubectl apply -f -
