#!/usr/bin/env bash
set -euo pipefail
context="${ASTRONA_KUBE_CONTEXT:-kind-astro-ats-031-lab-010-03-03}"
cluster="${ASTRONA_KIND_CLUSTER:-astro-ats-031-lab-010-03-03}"
engine="${ASTRONA_CONTAINER_ENGINE:-podman}"
[[ "$(kubectl config current-context)" == "$context" ]] || { echo 'ERROR: wrong context'; exit 2; }
lab_directory="$(cd "$(dirname "$0")/.." && pwd)"
for outcome in address-exception port-range; do python3 "$lab_directory/testing/grade.py" "$outcome"; done
kubectl -n ranges-training create networkpolicy --help >/dev/null
kubectl -n ranges-training apply -f "$lab_directory/testing/bypass.yaml"
sleep 3
set +e
output=$(python3 "$lab_directory/testing/grade.py" port-range); status=$?
set -e
[[ "$status" == 1 && "$output" == 'FAIL: Reject both neighboring ports' ]]
kubectl -n ranges-training delete networkpolicy bypass
sleep 3
