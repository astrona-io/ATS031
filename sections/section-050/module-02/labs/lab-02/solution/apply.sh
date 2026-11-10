#!/usr/bin/env bash
# Reference result, applied only by astrona test. Kept in step with solution.md.
set -euo pipefail
context="${ASTRONA_KUBE_CONTEXT:-kind-astro-ats-031-lab-050-02-02}"
if [[ "$(kubectl config current-context)" != "$context" ]]; then
  printf 'Refusing to operate on another Kubernetes context\n' >&2
  exit 1
fi
cluster="${ASTRONA_KIND_CLUSTER:-astro-ats-031-lab-050-02-02}"
engine="${ASTRONA_CONTAINER_ENGINE:-podman}"
CONTROL="$cluster-control-plane"
WORKER="$cluster-worker"
pid="$("$engine" exec "$WORKER" sh -c "grep -l '^kubelet\$' /proc/[0-9]*/comm | head -n 1 | cut -d/ -f3")"
path="$("$engine" exec "$WORKER" readlink "/proc/$pid/exe")"
version="$("$engine" exec "$WORKER" "$path" --version | awk '{print $NF}')"
actual="$("$engine" exec "$WORKER" sha256sum "$path" | cut -d' ' -f1)"
published="$("$engine" exec "$WORKER" sh -c "cat /var/lib/training-release/k8s/release/$version/bin/linux/*/kubelet.sha256")"
result=mismatch
if [[ "$published" == "$actual" ]]; then result=match; fi
kubectl -n starfleet-031-050-02-02 create configmap kubelet-review --from-literal=version="$version" --from-literal=path="$path" --from-literal=sha256="$actual" --from-literal=result="$result" --dry-run=client -o yaml | kubectl apply -f -
