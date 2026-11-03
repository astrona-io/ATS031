#!/usr/bin/env bash
# Reference result, applied only by astrona test. Kept in step with solution.md.
set -euo pipefail
CONTROL="astro-ats-031-lab-050-03-02-control-plane"
WORKER="astro-ats-031-lab-050-03-02-worker"
if [[ "$(kubectl config current-context)" != "kind-astro-ats-031-lab-050-03-02" ]]; then
  printf "Refusing to operate on another Kubernetes context
" >&2
  exit 1
fi
image_id="$(kubectl -n starfleet get pods -l app=relay -o jsonpath='{.items[0].status.containerStatuses[0].imageID}')"
digest="sha256:${image_id##*sha256:}"
kubectl -n starfleet set image deployment/relay "relay=docker.io/library/busybox:1.37.0@$digest"
kubectl -n starfleet rollout status deployment/relay --timeout=180s
new_id="$(kubectl -n starfleet get pods -l app=relay -o jsonpath='{.items[0].status.containerStatuses[0].imageID}')"
kubectl -n starfleet create configmap image-pin-review --from-literal=digest="$digest" --from-literal=imageID="$new_id" --dry-run=client -o yaml | kubectl apply -f -
