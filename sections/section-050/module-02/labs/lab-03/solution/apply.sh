#!/usr/bin/env bash
# Reference solution: compare every binary with its published digest and
# record the one that does not match.
set -euo pipefail
context="${ASTRONA_KUBE_CONTEXT:-kind-astro-ats-031-lab-050-02-03}"
if [[ "$(kubectl config current-context)" != "$context" ]]; then
  printf 'Refusing to operate on another Kubernetes context\n' >&2
  exit 1
fi
cluster="${ASTRONA_KIND_CLUSTER:-astro-ats-031-lab-050-02-03}"
engine="${ASTRONA_CONTAINER_ENGINE:-podman}"
node_name="$cluster-control-plane"
bundle=/var/lib/node-bundle
for binary in kube-apiserver kube-controller-manager kube-scheduler kube-proxy kubectl kubeadm kubelet; do
  published_digest=$("$engine" exec "$node_name" cat "$bundle/$binary.sha256")
  if ! printf '%s  %s\n' "$published_digest" "$binary" | "$engine" exec -i -w "$bundle" "$node_name" sha256sum --check --status; then
    failing_binary="$binary"
  fi
done
kubectl -n starfleet-031-050-02-03 create configmap failing-binary \
  --from-literal=name="$failing_binary" --dry-run=client -o yaml | kubectl apply -f -
