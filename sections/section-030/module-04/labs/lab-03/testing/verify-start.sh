#!/usr/bin/env bash
set -euo pipefail
context="${ASTRONA_KUBE_CONTEXT:-kind-astro-ats-031-lab-030-04-03}"
cluster="${ASTRONA_KIND_CLUSTER:-astro-ats-031-lab-030-04-03}"
engine="${ASTRONA_CONTAINER_ENGINE:-podman}"
[[ "$(kubectl config current-context)" == "$context" ]] || { echo 'ERROR: wrong context'; exit 2; }
lab_directory="$(cd "$(dirname "$0")/.." && pwd)"
for outcome in replacement-secret served-certificate; do
  set +e
  output=$(python3 "$lab_directory/testing/grade.py" "$outcome" 2>&1); status=$?
  set -e
  printf '%s\n' "$output"
  [[ "$status" == 1 && "$output" == FAIL:* ]] || exit 2
done
