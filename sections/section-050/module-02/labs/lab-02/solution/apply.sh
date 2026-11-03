#!/usr/bin/env bash
# Reference result, applied only by astrona test. Kept in step with solution.md.
set -euo pipefail
CONTROL="astro-ats-031-lab-050-02-02-control-plane"
WORKER="astro-ats-031-lab-050-02-02-worker"
if [[ "$(kubectl config current-context)" != "kind-astro-ats-031-lab-050-02-02" ]]; then
  printf "Refusing to operate on another Kubernetes context
" >&2
  exit 1
fi
pid="$(podman exec "$WORKER" sh -c "grep -l '^kubelet\$' /proc/[0-9]*/comm | head -n 1 | cut -d/ -f3")"
path="$(podman exec "$WORKER" readlink "/proc/$pid/exe")"
version="$(podman exec "$WORKER" "$path" --version | awk '{print $NF}')"
actual="$(podman exec "$WORKER" sha256sum "$path" | cut -d' ' -f1)"
published="$(podman exec "$WORKER" sh -c "cat /var/lib/training-release/k8s/release/$version/bin/linux/*/kubelet.sha256")"
result=mismatch
if [[ "$published" == "$actual" ]]; then result=match; fi
kubectl -n starfleet create configmap kubelet-review --from-literal=version="$version" --from-literal=path="$path" --from-literal=sha256="$actual" --from-literal=result="$result" --dry-run=client -o yaml | kubectl apply -f -
