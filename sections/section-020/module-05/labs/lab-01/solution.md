---
exam_objectives:
- Use CIS benchmark to review the security configuration of Kubernetes components
  (etcd, kubelet, kubedns, kubeapi)
---
# Secure Kubelet Authentication And Authorization Solution

Connect to this lab from a host shell. The command `astrona kubeconfig` prints the path of the lab's kubeconfig, the file that tells `kubectl` which cluster to use and which credentials to send. The two variables hold the names of the node containers: `node_name` is the control plane node and `worker_name` is the worker node.

```sh
export KUBECONFIG="$(astrona kubeconfig ats-031-lab-020-05-01)"
test "$(kubectl config current-context)" = "kind-astro-ats-031-lab-020-05-01" || exit 1
node_name="astro-ats-031-lab-020-05-01-control-plane"
worker_name="astro-ats-031-lab-020-05-01-worker"
```

Run node commands as `podman exec "$node_name" ...` or `podman exec "$worker_name" ...`. They change only the node containers of this lab, not your own computer.

## See the open kubelet API

The kubelet API on port `10250` can list pods, read logs and run commands in containers. Send a request without credentials from the control plane node:

```sh
worker_ip="$(kubectl get node "$worker_name" -o jsonpath='{.status.addresses[?(@.type=="InternalIP")].address}')"
podman exec "$node_name" curl -sk --max-time 5 -o /dev/null -w '%{http_code}\n' "https://$worker_ip:10250/pods"
```

The answer is `200`: the kubelet accepts the anonymous request and allows it. Two settings work together here. Authentication decides who the caller is; with `anonymous.enabled: true`, a caller without credentials becomes the user `system:anonymous`. Authorization decides what the caller may do; `AlwaysAllow` allows everything.

## Change both settings

Keep a copy of the file, then change the two values:

```sh
podman exec "$worker_name" cp /var/lib/kubelet/config.yaml /root/kubelet-config.yaml.before
podman exec "$worker_name" sed -i '/^  anonymous:/{n;s/enabled: true/enabled: false/}' /var/lib/kubelet/config.yaml
podman exec "$worker_name" sed -i 's/^  mode: AlwaysAllow$/  mode: Webhook/' /var/lib/kubelet/config.yaml
podman exec "$worker_name" grep -A6 '^authentication:' /var/lib/kubelet/config.yaml
podman exec "$worker_name" grep -A1 '^authorization:' /var/lib/kubelet/config.yaml
podman exec "$worker_name" systemctl restart kubelet
```

The first `sed` command finds the line `anonymous:` and changes `enabled` on the next line. With `Webhook`, the kubelet sends each request to the API server as a `SubjectAccessReview` and follows its answer.

## Check the result

The kubelet reads its configuration only when it starts. Restart it, then read the effective configuration through the API server. The `configz` endpoint returns the values that the running kubelet really uses, after all sources are merged:

```sh
kubectl get --raw "/api/v1/nodes/$worker_name/proxy/configz" | python3 -m json.tool | grep -A2 -e '"anonymous"' -e '"authorization"'
podman exec "$node_name" curl -sk --max-time 5 -o /dev/null -w '%{http_code}\n' "https://$worker_ip:10250/pods"
kubectl get node "$worker_name"
```

`anonymous` shows `enabled: false`, the mode is `Webhook`, and the request now returns `401` (Unauthorized), because the kubelet no longer accepts a caller without credentials. The API server still reaches the kubelet with its own client certificate, so `kubectl logs` and `kubectl exec` keep working.

## Common pitfalls

> [!WARNING]
> With only `Webhook` and anonymous access still on, the request returns `403` instead of `401`; the caller is still accepted as `system:anonymous`. A changed file without a kubelet restart changes nothing. A typing mistake in `config.yaml` stops the kubelet; keep the copy so you can put it back.
