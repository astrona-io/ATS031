#!/usr/bin/env bash
# Reference result, applied only by astrona test. Kept in step with solution.md.
set -euo pipefail
CONTROL="astro-ats-031-capstone-050-control-plane"
WORKER="astro-ats-031-capstone-050-worker"
if [[ "$(kubectl config current-context)" != "kind-astro-ats-031-capstone-050" ]]; then
  printf "Refusing to operate on another Kubernetes context
" >&2
  exit 1
fi
B=/var/lib/training-release/bundle
A=/var/lib/training-release/approved
podman exec "$CONTROL" sh -c "cd $B && openssl dgst -sha256 -verify publisher.pub -signature SHA256SUMS.sig SHA256SUMS"
genuine=()
rejected=()
for tool in kubectl kubeadm; do
  if podman exec "$CONTROL" sh -c "cd $B && grep ' $tool\$' SHA256SUMS | sha256sum --check --status"; then
    genuine+=("$tool")
    podman exec "$CONTROL" cp "$B/$tool" "$A/$tool"
  else
    rejected+=("$tool")
  fi
done
pid="$(podman exec "$WORKER" sh -c "grep -l '^kubelet\$' /proc/[0-9]*/comm | head -n 1 | cut -d/ -f3")"
running="$(podman exec "$WORKER" sha256sum "/proc/$pid/exe" | cut -d' ' -f1)"
listed="$(podman exec "$CONTROL" sh -c "grep ' kubelet\$' $B/SHA256SUMS | cut -d' ' -f1")"
[[ "$running" == "$listed" ]]
image_id="$(kubectl -n starfleet get pods -l app=relay -o jsonpath='{.items[0].status.containerStatuses[0].imageID}')"
image="docker.io/library/busybox:1.37.0@sha256:${image_id##*sha256:}"
kubectl -n starfleet set image deployment/relay "relay=$image"
kubectl -n starfleet rollout status deployment/relay --timeout=180s
kubectl -n starfleet create configmap verification-report \
  --from-literal=manifest_signature=verified \
  --from-literal=genuine="$(IFS=,; echo "${genuine[*]}")" \
  --from-literal=rejected="$(IFS=,; echo "${rejected[*]}")" \
  --from-literal=kubelet=match \
  --from-literal=kubelet_sha256="$running" \
  --from-literal=image="$image" --dry-run=client -o yaml | kubectl apply -f -
