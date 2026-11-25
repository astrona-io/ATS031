#!/usr/bin/env bash
set -euo pipefail
if [[ "$(kubectl config current-context)" != "kind-astro-ats-031-playground-010-04" ]]; then
  printf 'Refusing to operate on another Kubernetes context\n' >&2
  exit 1
fi
lab_directory="$(cd "$(dirname "$0")/.." && pwd)"
for attempt in 1 2 3 4 5 6 7 8 9 10; do
  if bash "$lab_directory/validate.sh"; then exit 0; fi
  sleep 2
done
printf 'Playground fixtures did not pass the check within the bounded retry period\n' >&2
exit 1
