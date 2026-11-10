#!/usr/bin/env bash
# Reference result, applied only by astrona test. Kept in step with solution.md.
set -euo pipefail
context="${ASTRONA_KUBE_CONTEXT:-kind-astro-ats-031-lab-050-03-01}"
if [[ "$(kubectl config current-context)" != "$context" ]]; then
  printf 'Refusing to operate on another Kubernetes context\n' >&2
  exit 1
fi
cluster="${ASTRONA_KIND_CLUSTER:-astro-ats-031-lab-050-03-01}"
engine="${ASTRONA_CONTAINER_ENGINE:-podman}"
CONTROL="$cluster-control-plane"
WORKER="$cluster-worker"
D=/var/lib/training-release/signed/lab
if "$engine" exec "$CONTROL" sh -c "cd $D && gpg --no-default-keyring --keyring ./publisher.gpg --verify gpg-notes.txt.asc gpg-notes.txt" >/dev/null 2>&1; then
  forged=cosign
else
  forged=gpg
fi
"$engine" exec "$CONTROL" sh -c "printf '%s\n' $forged > $D/result.txt"
