#!/usr/bin/env bash
set -euo pipefail
context="${ASTRONA_KUBE_CONTEXT:-kind-astro-ats-031-lab-020-05-02}"
if [[ "$(kubectl config current-context)" != "$context" ]]; then
  printf 'Refusing to operate on another Kubernetes context\n' >&2
  exit 1
fi
cluster="${ASTRONA_KIND_CLUSTER:-astro-ats-031-lab-020-05-02}"
engine="${ASTRONA_CONTAINER_ENGINE:-podman}"
lab_directory="$(cd "$(dirname "$0")/.." && pwd)"
node_name="$cluster-control-plane"
worker_name="$cluster-worker"
set_kubelet_field() {
  "$engine" exec "$worker_name" sed -i "/^$1:/d" /var/lib/kubelet/config.yaml
  "$engine" exec "$worker_name" sh -c "printf '\n%s: %s\n' '$1' '$2' >> /var/lib/kubelet/config.yaml"
}
"$engine" exec "$worker_name" chmod 600 /var/lib/kubelet/config.yaml /etc/kubernetes/kubelet.conf
set_kubelet_field rotateCertificates true
set_kubelet_field streamingConnectionIdleTimeout 5m
set_kubelet_field tlsMinVersion VersionTLS12
"$engine" exec "$worker_name" systemctl restart kubelet
settled=0
for attempt in $(seq 1 60); do
  if kubectl --request-timeout=3s get --raw "/api/v1/nodes/$worker_name/proxy/configz" 2>/dev/null | grep -q '"tlsMinVersion":"VersionTLS12"'; then settled=1; break; fi
  sleep 3
done
test "$settled" -eq 1
