#!/usr/bin/env bash
set -euo pipefail
if [[ "$(kubectl config current-context)" != "kind-astro-ats-031-lab-020-05-02" ]]; then
  printf 'Refusing to operate on another Kubernetes context\n' >&2
  exit 1
fi
lab_directory="$(cd "$(dirname "$0")/.." && pwd)"
node_name="astro-ats-031-lab-020-05-02-control-plane"
worker_name="astro-ats-031-lab-020-05-02-worker"
set_kubelet_field() {
  podman exec "$worker_name" sed -i "/^$1:/d" /var/lib/kubelet/config.yaml
  podman exec "$worker_name" sh -c "printf '\n%s: %s\n' '$1' '$2' >> /var/lib/kubelet/config.yaml"
}
podman exec "$worker_name" chmod 600 /var/lib/kubelet/config.yaml /etc/kubernetes/kubelet.conf
set_kubelet_field rotateCertificates true
set_kubelet_field streamingConnectionIdleTimeout 5m
set_kubelet_field tlsMinVersion VersionTLS12
podman exec "$worker_name" systemctl restart kubelet
settled=0
for attempt in $(seq 1 60); do
  if kubectl --request-timeout=3s get --raw "/api/v1/nodes/$worker_name/proxy/configz" 2>/dev/null | grep -q '"tlsMinVersion":"VersionTLS12"'; then settled=1; break; fi
  sleep 3
done
test "$settled" -eq 1
