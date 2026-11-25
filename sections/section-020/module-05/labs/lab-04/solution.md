---
exam_objectives:
- Use CIS benchmark to review the security configuration of Kubernetes components
  (etcd, kubelet, kubedns, kubeapi)
---
# Close The Kubelet Read-Only Port And Raise Its TLS Minimum Solution

Open a shell on the lab VM (virtual machine) and check that kubectl uses this lab's cluster:

```sh
astrona ssh astro-ats-031-lab-020-05-04
kubectl config current-context
```

The second command prints `kubernetes-admin@astro-ats-031-lab-020-05-04`. You are logged in as the `student` user, which has a kubeconfig file for the cluster. A kubeconfig file tells `kubectl` which cluster to use and which credentials to send. Node files and processes belong to root, so run node commands with `sudo`. They change only the lab VM, not your own computer.

## See the open port

The read-only port serves parts of the kubelet API over plain HTTP, without authentication and without authorization. Read the address of the node and send a request from the `shuttle` pod:

```sh
node_ip="$(kubectl get node "astro-ats-031-lab-020-05-04" -o jsonpath='{.status.addresses[?(@.type=="InternalIP")].address}')"
kubectl -n starfleet-031-020-05-04 exec shuttle -- wget -q -T 3 -O- "http://$node_ip:10255/pods" | head -c 200; echo
kubectl get --raw "/api/v1/nodes/astro-ats-031-lab-020-05-04/proxy/configz" | python3 -m json.tool | grep -e readOnlyPort -e tlsMinVersion
```

The first command prints the start of a JSON pod list. The effective configuration shows `readOnlyPort` `10255` and `tlsMinVersion` `VersionTLS10`.

## Change the two fields

The kubelet stops at start when a key appears twice in its file, so delete each key before you add it again:

```sh
sudo cp /var/lib/kubelet/config.yaml /root/kubelet-config.yaml.before
sudo sed -i -e '/^readOnlyPort:/d' -e '/^tlsMinVersion:/d' /var/lib/kubelet/config.yaml
sudo sh -c "printf '\nreadOnlyPort: 0\ntlsMinVersion: VersionTLS12\n' >> /var/lib/kubelet/config.yaml"
sudo grep -e readOnlyPort -e tlsMinVersion /var/lib/kubelet/config.yaml
sudo systemctl restart kubelet
```

`readOnlyPort: 0` turns the port off. `tlsMinVersion` sets the lowest TLS version that the kubelet accepts on port `10250`; TLS 1.0 and 1.1 have known weaknesses.

## Check the result

The kubelet reads its configuration only when it starts. Restart it, then read the effective configuration through the API server. The `configz` endpoint returns the values that the running kubelet really uses, after all sources are merged:

```sh
kubectl get --raw "/api/v1/nodes/astro-ats-031-lab-020-05-04/proxy/configz" | python3 -m json.tool | grep -e readOnlyPort -e tlsMinVersion
kubectl -n starfleet-031-020-05-04 exec shuttle -- wget -q -T 3 -O- "http://$node_ip:10255/pods"; echo "exit code $?"
kubectl get node "astro-ats-031-lab-020-05-04"
```

`tlsMinVersion` is `VersionTLS12`. `readOnlyPort` no longer appears, because the endpoint leaves out fields with the value `0`. The `wget` command fails with an exit code other than `0`, and the node is `Ready`.

## Common pitfalls

> [!WARNING]
> A second `readOnlyPort` line instead of a replaced one stops the kubelet. `readOnlyPort` missing from `configz` means `0`, not an error. The TLS values are names such as `VersionTLS12`, not numbers such as `1.2`.
