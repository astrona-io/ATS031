---
draft: true
exam_objectives:
- Use CIS benchmark to review the security configuration of Kubernetes components
  (etcd, kubelet, kubedns, kubeapi)
---
# Close Anonymous And Open Access On The Kubelet Solution

Use a host shell with the private kubeconfig for this independent kind environment. A kubeconfig identifies the cluster and credentials used by kubectl, the Kubernetes command-line tool.

```sh
export KUBECONFIG="$(astrona kubeconfig ats-031-lab-020-05-01)"
test "$(kubectl config current-context)" = "kind-astro-ats-031-lab-020-05-01" || exit 1
node_name="astro-ats-031-lab-020-05-01-control-plane"
worker_name="astro-ats-031-lab-020-05-01-worker"
```

Keep this connection selected. Host-level commands name only this environment's node containers. They do not operate on the host operating system.

## Inspect

Read the three effective settings through the API server:

```sh
kubectl get --raw "/api/v1/nodes/$worker_name/proxy/configz" | python3 -m json.tool | grep -e anonymous -e '"mode"' -e readOnlyPort
```

The output shows anonymous access enabled, the mode `AlwaysAllow` and the port `10255`.

## Change the kubelet file

Three commands change the file. The first two edit existing lines. The third removes the old `readOnlyPort` line and appends a new one, so the key appears once:

```sh
podman exec "$worker_name" sed -i '/^  anonymous:/{n;s/enabled: true/enabled: false/}' /var/lib/kubelet/config.yaml
podman exec "$worker_name" sed -i 's/^  mode: AlwaysAllow$/  mode: Webhook/' /var/lib/kubelet/config.yaml
podman exec "$worker_name" sed -i '/^readOnlyPort:/d' /var/lib/kubelet/config.yaml
podman exec "$worker_name" sh -c "printf '\nreadOnlyPort: 0\n' >> /var/lib/kubelet/config.yaml"
```

## Restart and wait

Restart the kubelet. Then ask the API server for the effective configuration until the anonymous setting shows `false`. The loop ignores errors while the kubelet restarts and stops after 60 tries:

```sh
podman exec "$worker_name" systemctl restart kubelet
for attempt in $(seq 1 60); do
  if kubectl --request-timeout=3s get --raw "/api/v1/nodes/$worker_name/proxy/configz" 2>/dev/null | grep -q '"anonymous":{"enabled":false}'; then echo "settled"; break; fi
  sleep 3
done
```

If the loop never prints the message, read the kubelet log with `podman exec "$worker_name" journalctl -u kubelet --no-pager -n 30`. The usual cause is a duplicate or misindented key. Copy the backup from `/opt/training/backup` over the file and start again.

## Verify

Read the settings again and check the node:

```sh
kubectl get --raw "/api/v1/nodes/$worker_name/proxy/configz" | python3 -m json.tool | grep -e anonymous -e '"mode"' -e readOnlyPort
kubectl get node "$worker_name"
```

The mode is `Webhook`, anonymous access is disabled, `readOnlyPort` is absent because the kubelet omits a zero value, and the node is `Ready`. Run `astrona submit` when this is true.
