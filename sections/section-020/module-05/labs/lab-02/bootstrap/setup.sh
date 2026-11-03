#!/usr/bin/env bash
set -euo pipefail
if [[ "$(kubectl config current-context)" != "kind-astro-ats-031-lab-020-05-02" ]]; then
  printf 'Refusing to operate on another Kubernetes context\n' >&2
  exit 1
fi
env_directory="$(cd "$(dirname "$0")/.." && pwd)"
node_name="astro-ats-031-lab-020-05-02-control-plane"
worker_name="astro-ats-031-lab-020-05-02-worker"
kubectl apply -f "$env_directory/bootstrap/manifests/start.yaml"
kubectl -n starfleet rollout status deployment/probe --timeout=180s
kubectl -n starfleet wait --for=condition=Ready pod/shuttle --timeout=120s
kubectl -n outpost wait --for=condition=Ready pod/drifter --timeout=120s
podman exec "$node_name" mkdir -p /opt/training/backup
podman exec "$node_name" cp /etc/kubernetes/manifests/kube-apiserver.yaml /etc/kubernetes/manifests/etcd.yaml /opt/training/backup/
podman exec "$worker_name" mkdir -p /opt/training/backup
podman exec "$worker_name" cp /var/lib/kubelet/config.yaml /opt/training/backup/kubelet-config.yaml
if [[ -n "${KUBE_BENCH_DIR:-}" && -d "$KUBE_BENCH_DIR" ]]; then
  podman cp "$KUBE_BENCH_DIR" "$worker_name:/opt/training/kube-bench"
fi
set_kubelet_field() {
  podman exec "$worker_name" sed -i "/^$1:/d" /var/lib/kubelet/config.yaml
  podman exec "$worker_name" sh -c "printf '\n%s: %s\n' '$1' '$2' >> /var/lib/kubelet/config.yaml"
}
podman exec "$worker_name" sed -i '/^  anonymous:/{n;s/enabled: false/enabled: true/}' /var/lib/kubelet/config.yaml
podman exec "$worker_name" sed -i 's/^  mode: Webhook$/  mode: AlwaysAllow/' /var/lib/kubelet/config.yaml
set_kubelet_field readOnlyPort 10255
podman exec "$worker_name" chmod 644 /var/lib/kubelet/config.yaml /etc/kubernetes/kubelet.conf
set_kubelet_field rotateCertificates false
set_kubelet_field streamingConnectionIdleTimeout 0s
podman exec "$worker_name" sed -i '/^tlsMinVersion:/d' /var/lib/kubelet/config.yaml
podman exec "$worker_name" systemctl restart kubelet
settled=0
for attempt in $(seq 1 60); do
  if kubectl --request-timeout=3s get --raw "/api/v1/nodes/$worker_name/proxy/configz" 2>/dev/null | grep -q '"readOnlyPort":10255'; then settled=1; break; fi
  sleep 3
done
test "$settled" -eq 1
