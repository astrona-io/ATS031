#!/usr/bin/env bash
set -euo pipefail
context="${ASTRONA_KUBE_CONTEXT:-kind-astro-ats-031-lab-020-02-01}"
if [[ "$(kubectl config current-context)" != "$context" ]]; then
  printf 'Refusing to operate on another Kubernetes context\n' >&2
  exit 1
fi
cluster="${ASTRONA_KIND_CLUSTER:-astro-ats-031-lab-020-02-01}"
engine="${ASTRONA_CONTAINER_ENGINE:-podman}"
lab_directory="$(cd "$(dirname "$0")/.." && pwd)"
node_name="$cluster-control-plane"
worker_name="$cluster-worker"
namespace="starfleet-031-020-02-01"
source "$lab_directory/bootstrap/helpers.sh"
if [[ "$("$engine" inspect "$node_name" --format '{{index .Config.Labels "io.x-k8s.kind.cluster"}}')" != "$cluster" ]]; then
  printf 'Refusing to operate on an unrelated node container\n' >&2
  exit 1
fi
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
