#!/usr/bin/env bash
set -euo pipefail
context="${ASTRONA_KUBE_CONTEXT:-kind-astro-ats-031-lab-040-02-02}"
if [[ "$(kubectl config current-context)" != "$context" ]]; then
  printf 'Refusing to operate on another Kubernetes context\n' >&2
  exit 1
fi
cluster="${ASTRONA_KIND_CLUSTER:-astro-ats-031-lab-040-02-02}"
engine="${ASTRONA_CONTAINER_ENGINE:-podman}"
lab_directory="$(cd "$(dirname "$0")/.." && pwd)"
worker_name="$cluster-worker"

# Give the worker node the link-local metadata address. The fake server binds to it.
"$engine" exec "$worker_name" sh -c "ip addr show dev lo | grep -q 169.254.169.254 || ip addr add 169.254.169.254/32 dev lo"

# Let pods reach host addresses on the worker, so the node-bound paths are testable.
# Best effort: the object name and kind depend on how Calico was installed.
kubectl patch felixconfigurations.crd.projectcalico.org default --type merge -p '{"spec":{"defaultEndpointToHostAction":"Accept"}}' >/dev/null 2>&1 \
  || kubectl patch felixconfiguration default --type merge -p '{"spec":{"defaultEndpointToHostAction":"Accept"}}' >/dev/null 2>&1 \
  || printf 'Note: could not set the Calico host action; pod-to-node paths may be dropped\n' >&2

kubectl apply -f "$lab_directory/bootstrap/manifests/start.yaml"
kubectl -n metadata-stub-031-040-02-02 wait --for=condition=Ready pod/fake-imds --timeout=180s
kubectl -n metadata-stub-031-040-02-02 wait --for=condition=Ready pod/control --timeout=120s
for namespace in starfleet-031-040-02-02 outpost-031-040-02-02 dock-031-040-02-02; do
  kubectl -n "$namespace" rollout status deployment/probe --timeout=180s
done
kubectl -n starfleet-031-040-02-02 wait --for=condition=Ready pod/shuttle pod/agent --timeout=120s
kubectl -n outpost-031-040-02-02 wait --for=condition=Ready pod/drifter --timeout=120s
kubectl -n dock-031-040-02-02 wait --for=condition=Ready pod/tender --timeout=120s

# Sanity check: an unrestricted pod must reach the fake metadata server.
for attempt in $(seq 1 10); do
  status="$(kubectl -n metadata-stub-031-040-02-02 exec control -- curl -s -m 3 -o /dev/null -w '%{http_code}' http://169.254.169.254/latest/meta-data/ || true)"
  if [[ "$status" == "200" ]]; then exit 0; fi
  sleep 3
done
printf 'Warning: the fake metadata server did not answer an unrestricted pod\n' >&2
