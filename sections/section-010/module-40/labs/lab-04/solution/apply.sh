#!/usr/bin/env bash
set -euo pipefail
context="${ASTRONA_KUBE_CONTEXT:-kind-astro-ats-031-lab-010-04-04}"
if [[ "$(kubectl config current-context)" != "$context" ]]; then
  printf 'Refusing to operate on another Kubernetes context\n' >&2
  exit 1
fi
solution_directory="$(cd "$(dirname "$0")" && pwd)"
namespace="starfleet-031-010-04-04"
outpost="outpost-031-010-04-04"
pod_address() { kubectl -n "$1" get pod "$2" -o jsonpath='{.status.podIP}'; }
check_path() { kubectl -n "$1" exec "$2" -- python /app/client.py tcp "$(pod_address "$3" "$4")" 8080 | cut -d' ' -f1; }
check_dns() { kubectl -n "$1" exec "$2" -- python /app/client.py dns kubernetes.default.svc.cluster.local | cut -d' ' -f1; }
kubectl -n "$namespace" create configmap test-matrix \
  --from-literal=rover-to-hangar="$(check_path "$namespace" rover "$namespace" hangar)" \
  --from-literal=rover-to-vault="$(check_path "$namespace" rover "$namespace" vault)" \
  --from-literal=tanker-to-hangar="$(check_path "$namespace" tanker "$namespace" hangar)" \
  --from-literal=drone-to-hangar="$(check_path "$outpost" drone "$namespace" hangar)" \
  --from-literal=drone-to-vault="$(check_path "$outpost" drone "$namespace" vault)" \
  --from-literal=rover-dns="$(check_dns "$namespace" rover)" \
  --from-literal=tanker-dns="$(check_dns "$namespace" tanker)" \
  --dry-run=client -o yaml | kubectl apply -f -
