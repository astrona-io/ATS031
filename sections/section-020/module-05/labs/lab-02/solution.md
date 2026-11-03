---
draft: true
exam_objectives:
- Use CIS benchmark to review the security configuration of Kubernetes components
  (etcd, kubelet, kubedns, kubeapi)
---
# Remediate Five Kubelet Benchmark Findings Solution

Use a host shell with the private kubeconfig for this independent kind environment. A kubeconfig identifies the cluster and credentials used by kubectl, the Kubernetes command-line tool.

```sh
export KUBECONFIG="$(astrona kubeconfig ats-031-lab-020-05-02)"
test "$(kubectl config current-context)" = "kind-astro-ats-031-lab-020-05-02" || exit 1
node_name="astro-ats-031-lab-020-05-02-control-plane"
worker_name="astro-ats-031-lab-020-05-02-worker"
```

Keep this connection selected. Host-level commands name only this environment's node containers. They do not operate on the host operating system.

## Inspect

Read the file modes and the effective values:

```sh
podman exec "$worker_name" stat -c '%a %n' /var/lib/kubelet/config.yaml /etc/kubernetes/kubelet.conf
kubectl get --raw "/api/v1/nodes/$worker_name/proxy/configz" | python3 -m json.tool | grep -e rotateCertificates -e streamingConnectionIdleTimeout -e tlsMinVersion
```

## Fix the file modes

```sh
podman exec "$worker_name" chmod 600 /var/lib/kubelet/config.yaml /etc/kubernetes/kubelet.conf
podman exec "$worker_name" stat -c '%a %n' /var/lib/kubelet/config.yaml /etc/kubernetes/kubelet.conf
```

Both files now show mode `600`.

## Fix the three settings

Define a helper that removes a key and appends it again, so the key appears once. Then set the three values:

```sh
set_kubelet_field() {
  podman exec "$worker_name" sed -i "/^$1:/d" /var/lib/kubelet/config.yaml
  podman exec "$worker_name" sh -c "printf '\n%s: %s\n' '$1' '$2' >> /var/lib/kubelet/config.yaml"
}
set_kubelet_field rotateCertificates true
set_kubelet_field streamingConnectionIdleTimeout 5m
set_kubelet_field tlsMinVersion VersionTLS12
```

## Restart and wait

Restart the kubelet and wait until the effective configuration shows the new value. The loop ignores errors while the kubelet restarts and stops after 60 tries:

```sh
podman exec "$worker_name" systemctl restart kubelet
for attempt in $(seq 1 60); do
  if kubectl --request-timeout=3s get --raw "/api/v1/nodes/$worker_name/proxy/configz" 2>/dev/null | grep -q '"tlsMinVersion":"VersionTLS12"'; then echo "settled"; break; fi
  sleep 3
done
```

If the loop never prints the message, read the kubelet log with `podman exec "$worker_name" journalctl -u kubelet --no-pager -n 30` and look for a duplicate key.

## Verify

Read the values again and check the node:

```sh
kubectl get --raw "/api/v1/nodes/$worker_name/proxy/configz" | python3 -m json.tool | grep -e rotateCertificates -e streamingConnectionIdleTimeout -e tlsMinVersion
kubectl get node "$worker_name"
```

The output shows `true`, `5m0s` and `VersionTLS12`, and the node is `Ready`. Run `astrona submit` when this is true.
