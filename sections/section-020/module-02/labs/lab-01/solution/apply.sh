#!/usr/bin/env bash
set -euo pipefail
context="${ASTRONA_KUBE_CONTEXT:-kubernetes-admin@astro-ats-031-lab-020-02-01}"
if [[ "$(kubectl config current-context)" != "$context" ]]; then
  printf 'Refusing to operate on another Kubernetes context\n' >&2
  exit 1
fi
cluster="astro-ats-031-lab-020-02-01"
lab_directory="$(cd "$(dirname "$0")/.." && pwd)"
# The VM is the only node: control plane and worker. kubeadm names it after
# the host name, which differs under `astrona test`.
node_name="$(hostname)"
worker_name="$node_name"
namespace="starfleet-031-020-02-01"
source "$lab_directory/bootstrap/helpers.sh"
solution_directory="$lab_directory/solution"
work_file="$(mktemp)"
kubectl apply -f "$solution_directory/job-api-server-audit.yaml"
kubectl -n "$namespace" wait --for=condition=complete job/api-server-audit --timeout=180s
kubectl -n "$namespace" logs job/api-server-audit | python3 -c '
import json, sys
text = sys.stdin.read()
report, _ = json.JSONDecoder().raw_decode(text[text.index("{"):])
found = set()
def walk(node):
    if isinstance(node, dict):
        if node.get("status") == "FAIL" and str(node.get("test_number", "")).startswith("1.2."):
            found.add(str(node["test_number"]))
        for value in node.values():
            walk(value)
    elif isinstance(node, list):
        for value in node:
            walk(value)
walk(report)
print("\n".join(sorted(found)))
' > "$work_file"
kubectl -n "$namespace" create configmap failing-checks --from-file=ids="$work_file" --dry-run=client -o yaml | kubectl apply -f -
rm -f "$work_file"
