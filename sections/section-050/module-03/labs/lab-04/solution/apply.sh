#!/usr/bin/env bash
# Reference solution: read the digest from the imageID of the running relay
# pod, pin the Deployment to it, wait for the rollout and record the result.
set -euo pipefail
context="${ASTRONA_KUBE_CONTEXT:-kind-astro-ats-031-lab-050-03-04}"
if [[ "$(kubectl config current-context)" != "$context" ]]; then
  printf 'Refusing to operate on another Kubernetes context\n' >&2
  exit 1
fi
namespace=starfleet-031-050-03-04
image_id=$(kubectl -n "$namespace" get pods -l app=relay -o jsonpath='{.items[0].status.containerStatuses[0].imageID}')
printf 'Running imageID: %s\n' "$image_id"
digest="sha256:${image_id##*@sha256:}"
kubectl -n "$namespace" set image deployment/relay relay="docker.io/library/python:3.13-alpine@$digest"
kubectl -n "$namespace" rollout status deployment/relay --timeout=180s
for attempt in $(seq 1 30); do
  [[ "$(kubectl -n "$namespace" get pods -l app=relay --no-headers | wc -l)" -eq 1 ]] && break
  sleep 2
done
new_image_id=$(kubectl -n "$namespace" get pods -l app=relay -o jsonpath='{.items[0].status.containerStatuses[0].imageID}')
printf 'New imageID: %s\n' "$new_image_id"
kubectl -n "$namespace" create configmap image-pin-review --from-literal=digest="$digest" --from-literal=imageID="$new_image_id" \
  --dry-run=client -o yaml | kubectl apply -f -
