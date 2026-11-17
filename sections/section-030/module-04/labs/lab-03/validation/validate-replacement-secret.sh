#!/usr/bin/env bash
set -euo pipefail
context="${ASTRONA_KUBE_CONTEXT:-kind-astro-ats-031-lab-030-04-03}"
cluster="${ASTRONA_KIND_CLUSTER:-astro-ats-031-lab-030-04-03}"
engine="${ASTRONA_CONTAINER_ENGINE:-podman}"
[[ "$(kubectl config current-context)" == "$context" ]] || { echo 'ERROR: wrong context'; exit 2; }
lab_directory="$(cd "$(dirname "$0")/.." && pwd)"
python3 "$lab_directory/testing/grade.py" replacement-secret
