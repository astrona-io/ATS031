#!/usr/bin/env bash
# Reference result, applied only by astrona test. Kept in step with solution.md.
set -euo pipefail
context="${ASTRONA_KUBE_CONTEXT:-kind-astro-ats-031-lab-050-03-02}"
if [[ "$(kubectl config current-context)" != "$context" ]]; then
  printf 'Refusing to operate on another Kubernetes context\n' >&2
  exit 1
fi
cluster="${ASTRONA_KIND_CLUSTER:-astro-ats-031-lab-050-03-02}"
CONTROL="$cluster-control-plane"
WORKER="$cluster-worker"
image_id="$(kubectl -n starfleet-031-050-03-02 get pods -l app=relay -o jsonpath='{.items[0].status.containerStatuses[0].imageID}')"
digest="sha256:${image_id##*sha256:}"
kubectl -n starfleet-031-050-03-02 set image deployment/relay "relay=docker.io/library/busybox:1.36.1@$digest"
kubectl -n starfleet-031-050-03-02 rollout status deployment/relay --timeout=180s
new_id="$(kubectl -n starfleet-031-050-03-02 get pods -l app=relay -o jsonpath='{.items[0].status.containerStatuses[0].imageID}')"
kubectl -n starfleet-031-050-03-02 create configmap image-pin-review --from-literal=digest="$digest" --from-literal=imageID="$new_id" --dry-run=client -o yaml | kubectl apply -f -
