#!/usr/bin/env bash
set -euo pipefail
context="${ASTRONA_KUBE_CONTEXT:-kind-astro-ats-031-lab-030-04-03}"
cluster="${ASTRONA_KIND_CLUSTER:-astro-ats-031-lab-030-04-03}"
engine="${ASTRONA_CONTAINER_ENGINE:-podman}"
[[ "$(kubectl config current-context)" == "$context" ]] || { echo 'ERROR: wrong context'; exit 2; }
lab_directory="$(cd "$(dirname "$0")/.." && pwd)"
for outcome in replacement-secret served-certificate; do python3 "$lab_directory/testing/grade.py" "$outcome"; done
kubectl -n rotation-training get secret probe-old -o json | python3 -c 'import json,sys; s=json.load(sys.stdin); print(json.dumps({"apiVersion":"v1","kind":"Secret","metadata":{"name":"probe-tls","namespace":"rotation-training"},"type":"kubernetes.io/tls","data":s["data"]}))' | kubectl apply -f -
set +e
output=$(python3 "$lab_directory/testing/grade.py" served-certificate); status=$?
set -e
[[ "$status" == 1 && "$output" == 'FAIL: Replace both fields of the active TLS Secret' ]]
bash "$lab_directory/solution/apply.sh"
