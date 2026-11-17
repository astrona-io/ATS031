#!/usr/bin/env bash
set -euo pipefail
context="${ASTRONA_KUBE_CONTEXT:-kind-astro-ats-031-capstone-020}"
if [[ "$(kubectl config current-context)" != "$context" ]]; then
  printf 'Refusing to operate on another Kubernetes context\n' >&2
  exit 1
fi
lab_directory="$(cd "$(dirname "$0")/.." && pwd)"
solution_directory="$lab_directory/solution"
cluster="${ASTRONA_KIND_CLUSTER:-astro-ats-031-capstone-020}"
node_name="$cluster-control-plane"
worker_name="$cluster-worker"
engine="${ASTRONA_CONTAINER_ENGINE:-podman}"
"$engine" exec "$node_name" chmod 700 /var/lib/etcd
python3 "$solution_directory/fix-api-server.py"
api_ready=0
for attempt in $(seq 1 80); do
  if kubectl --request-timeout=3s -n kube-system get pod "kube-apiserver-$node_name" -o jsonpath='{.spec.containers[0].command}' 2>/dev/null | grep -q -e 'encryption-provider-config' \
    && kubectl --request-timeout=3s get --raw=/readyz >/dev/null 2>&1; then api_ready=1; break; fi
  sleep 3
done
test "$api_ready" -eq 1
kubectl get secrets --all-namespaces -o json | kubectl replace -f -
set_kubelet_field() {
  "$engine" exec "$worker_name" sed -i "/^$1:/d" /var/lib/kubelet/config.yaml
  "$engine" exec "$worker_name" sh -c "printf '\n%s: %s\n' '$1' '$2' >> /var/lib/kubelet/config.yaml"
}
"$engine" exec "$worker_name" sed -i '/^  anonymous:/{n;s/enabled: true/enabled: false/}' /var/lib/kubelet/config.yaml
"$engine" exec "$worker_name" sed -i 's/^  mode: AlwaysAllow$/  mode: Webhook/' /var/lib/kubelet/config.yaml
set_kubelet_field readOnlyPort 0
"$engine" exec "$worker_name" systemctl restart kubelet
settled=0
for attempt in $(seq 1 60); do
  if kubectl --request-timeout=3s get --raw "/api/v1/nodes/$worker_name/proxy/configz" 2>/dev/null | grep -q '"anonymous":{"enabled":false}'; then settled=1; break; fi
  sleep 3
done
test "$settled" -eq 1
kubectl apply -f - <<'EVIDENCE'
apiVersion: v1
kind: ConfigMap
metadata:
  name: cis-evidence
  namespace: starfleet
data:
  apiserver-profiling: fixed
  etcd-data-dir: fixed
  etcd-encryption: fixed
  kubelet-anonymous-auth: fixed
  kubelet-authorization-mode: fixed
  kubelet-read-only-port: fixed
  before: "profiling enabled, data directory 755, Secrets in clear text, kubelet anonymous AlwaysAllow port 10255"
  after: "profiling disabled, data directory 700, Secrets encrypted, kubelet anonymous off Webhook port closed"
EVIDENCE
