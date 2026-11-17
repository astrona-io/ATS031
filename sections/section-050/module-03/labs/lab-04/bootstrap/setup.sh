#!/usr/bin/env bash
# Creates the lab namespace and the relay Deployment, which runs its image by
# tag, and waits until its pod runs.
#
# The preloaded image is imported into containerd without a repository digest,
# so the kubelet would report a bare image ID that cannot be used in a
# reference. On every node, this script adds the name
# docker.io/library/python@sha256:<manifest digest> to the imported image.
# The kubelet then reports that name as imageID, and a reference by that
# digest resolves locally, without any network access.
set -euo pipefail
context="${ASTRONA_KUBE_CONTEXT:-kind-astro-ats-031-lab-050-03-04}"
if [[ "$(kubectl config current-context)" != "$context" ]]; then
  printf 'Refusing to operate on another Kubernetes context\n' >&2
  exit 1
fi
cluster="${ASTRONA_KIND_CLUSTER:-astro-ats-031-lab-050-03-04}"
engine="${ASTRONA_CONTAINER_ENGINE:-podman}"
image=docker.io/library/python:3.13-alpine
lab_directory="$(cd "$(dirname "$0")/.." && pwd)"
for node in "$cluster-control-plane" "$cluster-worker"; do
  manifest_digest="$("$engine" exec "$node" ctr -n k8s.io images ls | awk -v name="$image" '$1 == name {print $3}')"
  if [[ "$manifest_digest" != sha256:* ]]; then
    printf 'Image %s is not loaded on %s\n' "$image" "$node" >&2
    exit 1
  fi
  "$engine" exec "$node" ctr -n k8s.io images rm "docker.io/library/python@$manifest_digest" >/dev/null 2>&1 || true
  "$engine" exec "$node" ctr -n k8s.io images tag "$image" "docker.io/library/python@$manifest_digest"
done
kubectl apply -f "$lab_directory/bootstrap/manifests/namespace.yaml"
kubectl apply -f "$lab_directory/bootstrap/manifests/deployment-relay.yaml"
kubectl -n starfleet-031-050-03-04 rollout status deployment/relay --timeout=180s
