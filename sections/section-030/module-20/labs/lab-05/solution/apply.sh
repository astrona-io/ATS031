#!/usr/bin/env bash
set -euo pipefail
context="${ASTRONA_KUBE_CONTEXT:-kind-astro-ats-031-lab-030-02-05}"
if [[ "$(kubectl config current-context)" != "$context" ]]; then
  printf 'Refusing to operate on another Kubernetes context\n' >&2
  exit 1
fi
lab_directory="$(cd "$(dirname "$0")/.." && pwd)"
solution_directory="$lab_directory/solution"
kubectl apply -f "$solution_directory/ingress-beacon.yaml"
router=""
for attempt in $(seq 1 30); do
  router="$(kubectl -n starfleet-031-030-02-05 exec deployment/probe -- python -c "import json, urllib.request; print(''.join(item['name'] for item in json.load(urllib.request.urlopen('http://traefik.ingress-system.svc:8080/api/http/routers')) if 'beacon.local' in item.get('rule', '')))")"
  if [[ -n "$router" ]]; then break; fi
  sleep 2
done
kubectl -n starfleet-031-030-02-05 create configmap route-evidence --from-literal=router="$router"
