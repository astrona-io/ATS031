#!/usr/bin/env bash
# Reference result, applied only by astrona test. Kept in step with solution.md.
set -euo pipefail
CONTROL="astro-ats-031-lab-050-03-01-control-plane"
WORKER="astro-ats-031-lab-050-03-01-worker"
if [[ "$(kubectl config current-context)" != "kind-astro-ats-031-lab-050-03-01" ]]; then
  printf "Refusing to operate on another Kubernetes context
" >&2
  exit 1
fi
D=/var/lib/training-release/signed/lab
if podman exec "$CONTROL" sh -c "cd $D && gpg --no-default-keyring --keyring ./publisher.gpg --verify gpg-notes.txt.asc gpg-notes.txt" >/dev/null 2>&1; then
  forged=cosign
else
  forged=gpg
fi
podman exec "$CONTROL" sh -c "printf '%s\n' $forged > $D/result.txt"
