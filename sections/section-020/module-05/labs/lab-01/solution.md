---
exam_objectives:
- Use CIS benchmark to review the security configuration of Kubernetes components
  (etcd, kubelet, kubedns, kubeapi)
---
# Secure Kubelet Authentication And Authorization Solution

Open a shell on the lab VM (virtual machine) and check that kubectl uses this lab's cluster:

```sh
astrona ssh astro-ats-031-lab-020-05-01
kubectl config current-context
```

The second command prints `kubernetes-admin@astro-ats-031-lab-020-05-01`. You are logged in as the `student` user, which has a kubeconfig file for the cluster. A kubeconfig file tells `kubectl` which cluster to use and which credentials to send. Node files and processes belong to root, so run node commands with `sudo`. They change only the lab VM, not your own computer.

## See the open kubelet API

The kubelet API on port `10250` can list pods, read logs and run commands in containers. Send a request without credentials from the node itself:

```sh
node_ip="$(kubectl get node "astro-ats-031-lab-020-05-01" -o jsonpath='{.status.addresses[?(@.type=="InternalIP")].address}')"
sudo curl -sk --max-time 5 -o /dev/null -w '%{http_code}\n' "https://$node_ip:10250/pods"
```

The answer is `200`: the kubelet accepts the anonymous request and allows it. Two settings work together here. Authentication decides who the caller is; with `anonymous.enabled: true`, a caller without credentials becomes the user `system:anonymous`. Authorization decides what the caller may do; `AlwaysAllow` allows everything.

## Change both settings

Keep a copy of the file, then change the two values:

```sh
sudo cp /var/lib/kubelet/config.yaml /root/kubelet-config.yaml.before
sudo sed -i '/^  anonymous:/{n;s/enabled: true/enabled: false/}' /var/lib/kubelet/config.yaml
sudo sed -i 's/^  mode: AlwaysAllow$/  mode: Webhook/' /var/lib/kubelet/config.yaml
sudo grep -A6 '^authentication:' /var/lib/kubelet/config.yaml
sudo grep -A1 '^authorization:' /var/lib/kubelet/config.yaml
sudo systemctl restart kubelet
```

The first `sed` command finds the line `anonymous:` and changes `enabled` on the next line. With `Webhook`, the kubelet sends each request to the API server as a `SubjectAccessReview` and follows its answer.

## Check the result

The kubelet reads its configuration only when it starts. Restart it, then read the effective configuration through the API server. The `configz` endpoint returns the values that the running kubelet really uses, after all sources are merged:

```sh
kubectl get --raw "/api/v1/nodes/astro-ats-031-lab-020-05-01/proxy/configz" | python3 -m json.tool | grep -A2 -e '"anonymous"' -e '"authorization"'
sudo curl -sk --max-time 5 -o /dev/null -w '%{http_code}\n' "https://$node_ip:10250/pods"
kubectl get node "astro-ats-031-lab-020-05-01"
```

`anonymous` shows `enabled: false`, the mode is `Webhook`, and the request now returns `401` (Unauthorized), because the kubelet no longer accepts a caller without credentials. The API server still reaches the kubelet with its own client certificate, so `kubectl logs` and `kubectl exec` keep working.

## Common pitfalls

> [!WARNING]
> With only `Webhook` and anonymous access still on, the request returns `403` instead of `401`; the caller is still accepted as `system:anonymous`. A changed file without a kubelet restart changes nothing. A typing mistake in `config.yaml` stops the kubelet; keep the copy so you can put it back.
