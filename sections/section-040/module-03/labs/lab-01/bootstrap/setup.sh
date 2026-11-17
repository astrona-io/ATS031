#!/usr/bin/env bash
set -euo pipefail
context="${ASTRONA_KUBE_CONTEXT:-kind-astro-ats-031-lab-040-03-01}"
if [[ "$(kubectl config current-context)" != "$context" ]]; then
  printf 'Refusing to operate on another Kubernetes context\n' >&2
  exit 1
fi
cluster="${ASTRONA_KIND_CLUSTER:-astro-ats-031-lab-040-03-01}"
engine="${ASTRONA_CONTAINER_ENGINE:-podman}"
lab_directory="$(cd "$(dirname "$0")/.." && pwd)"
worker_name="$cluster-worker"

# Open the kubelet read-only port on the worker on purpose. The learner closes it.
"$engine" exec "$worker_name" sh -c "if grep -q '^readOnlyPort:' /var/lib/kubelet/config.yaml; then sed -i 's/^readOnlyPort:.*/readOnlyPort: 10255/' /var/lib/kubelet/config.yaml; else echo 'readOnlyPort: 10255' >> /var/lib/kubelet/config.yaml; fi"
"$engine" exec "$worker_name" systemctl restart kubelet
sleep 10
kubectl wait --for=condition=Ready "node/$worker_name" --timeout=180s

# Let pods reach host addresses on the worker, so the node ports are testable.
# Best effort: the object name and kind depend on how Calico was installed.
kubectl patch felixconfigurations.crd.projectcalico.org default --type merge -p '{"spec":{"defaultEndpointToHostAction":"Accept"}}' >/dev/null 2>&1 \
  || kubectl patch felixconfiguration default --type merge -p '{"spec":{"defaultEndpointToHostAction":"Accept"}}' >/dev/null 2>&1 \
  || printf 'Note: could not set the Calico host action; pod-to-node paths may be dropped\n' >&2

kubectl apply -f "$lab_directory/bootstrap/manifests/start.yaml"
kubectl -n dock-031-040-03-01 wait --for=condition=Ready pod/inspector --timeout=180s
