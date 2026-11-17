#!/usr/bin/env bash
set -euo pipefail
context="${ASTRONA_KUBE_CONTEXT:-kind-astro-ats-031-lab-010-03-03}"
cluster="${ASTRONA_KIND_CLUSTER:-astro-ats-031-lab-010-03-03}"
engine="${ASTRONA_CONTAINER_ENGINE:-podman}"
[[ "$(kubectl config current-context)" == "$context" ]] || { echo 'ERROR: wrong context'; exit 2; }
lab_directory="$(cd "$(dirname "$0")/.." && pwd)"
excluded=$(kubectl -n ranges-training get pod excluded -o jsonpath='{.status.podIP}')
python3 - "$lab_directory/solution/policy.json" "$excluded" <<'APPLY'
import json,sys,subprocess
obj=json.load(open(sys.argv[1]));obj['spec']['ingress'][0]['from'][0]['ipBlock']['except']=[sys.argv[2]+'/32']
subprocess.run(['kubectl','apply','-f','-'],input=json.dumps(obj),text=True,check=True)
APPLY
sleep 3
