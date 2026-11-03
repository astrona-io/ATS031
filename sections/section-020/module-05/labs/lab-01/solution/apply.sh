#!/usr/bin/env bash
set -euo pipefail
if [[ "$(kubectl config current-context)" != "kind-astro-ats-031-lab-020-05-01" ]]; then
  printf 'Refusing to operate on another Kubernetes context\n' >&2
  exit 1
fi
lab_directory="$(cd "$(dirname "$0")/.." && pwd)"
node_name="astro-ats-031-lab-020-05-01-control-plane"
worker_name="astro-ats-031-lab-020-05-01-worker"
set_kubelet_field() {
  podman exec "$worker_name" sed -i "/^$1:/d" /var/lib/kubelet/config.yaml
  podman exec "$worker_name" sh -c "printf '\n%s: %s\n' '$1' '$2' >> /var/lib/kubelet/config.yaml"
}
podman exec "$worker_name" sed -i '/^  anonymous:/{n;s/enabled: true/enabled: false/}' /var/lib/kubelet/config.yaml
podman exec "$worker_name" sed -i 's/^  mode: AlwaysAllow$/  mode: Webhook/' /var/lib/kubelet/config.yaml
set_kubelet_field readOnlyPort 0
podman exec "$worker_name" systemctl restart kubelet
settled=0
for attempt in $(seq 1 60); do
  if kubectl --request-timeout=3s get --raw "/api/v1/nodes/$worker_name/proxy/configz" 2>/dev/null | grep -q '"anonymous":{"enabled":false}'; then settled=1; break; fi
  sleep 3
done
test "$settled" -eq 1
