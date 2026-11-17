---
exam_objectives:
- Use CIS benchmark to review the security configuration of Kubernetes components
  (etcd, kubelet, kubedns, kubeapi)
---
# Remove A Kubelet Flag That Overrides The Configuration File Solution

Connect to this lab from a host shell. The command `astrona kubeconfig` prints the path of the lab's kubeconfig, the file that tells `kubectl` which cluster to use and which credentials to send. The two variables hold the names of the node containers: `node_name` is the control plane node and `worker_name` is the worker node.

```sh
export KUBECONFIG="$(astrona kubeconfig ats-031-lab-020-05-03)"
test "$(kubectl config current-context)" = "kind-astro-ats-031-lab-020-05-03" || exit 1
node_name="astro-ats-031-lab-020-05-03-control-plane"
worker_name="astro-ats-031-lab-020-05-03-worker"
```

Run node commands as `podman exec "$node_name" ...` or `podman exec "$worker_name" ...`. They change only the node containers of this lab, not your own computer.

## Compare the file with the effective value

The kubelet takes its settings from three places: the configuration file, command-line flags and built-in defaults. A command-line flag wins over the file. Read the effective value first:

```sh
kubectl get --raw "/api/v1/nodes/$worker_name/proxy/configz" | python3 -m json.tool | grep -A2 '"authorization"'
```

The mode is `AlwaysAllow`, so the kubelet allows every request that passes authentication. Now read the configuration file:

```sh
podman exec "$worker_name" grep -A1 '^authorization:' /var/lib/kubelet/config.yaml
```

The file says `Webhook`. Something else sets the value.

## Find the source

systemd starts the kubelet. Its unit and the kubeadm drop-in file name the command line and the environment files that it reads:

```sh
podman exec "$worker_name" systemctl cat kubelet
podman exec "$worker_name" cat /var/lib/kubelet/kubeadm-flags.env
```

The drop-in file reads `/var/lib/kubelet/kubeadm-flags.env`, and the variable `KUBELET_KUBEADM_ARGS` in it holds `--authorization-mode=AlwaysAllow`. The running process shows the same flag:

```sh
podman exec "$worker_name" sh -c 'tr "\0" "\n" < /proc/$(pgrep -n kubelet)/cmdline' | grep -e authorization
```

## Remove the flag

Keep a copy, remove only the flag and restart the kubelet:

```sh
podman exec "$worker_name" cp /var/lib/kubelet/kubeadm-flags.env /root/kubeadm-flags.env.before
podman exec "$worker_name" sed -i 's|--authorization-mode=AlwaysAllow ||' /var/lib/kubelet/kubeadm-flags.env
podman exec "$worker_name" cat /var/lib/kubelet/kubeadm-flags.env
podman exec "$worker_name" systemctl restart kubelet
```

## Check the effective value

The kubelet reads its configuration only when it starts. Restart it, then read the effective configuration through the API server. The `configz` endpoint returns the values that the running kubelet really uses, after all sources are merged:

```sh
kubectl get --raw "/api/v1/nodes/$worker_name/proxy/configz" | python3 -m json.tool | grep -A2 '"authorization"'
kubectl get node "$worker_name"
```

The mode is now `Webhook`, so the kubelet asks the API server with a `SubjectAccessReview` whether each caller may do the request. The node is `Ready`. If the old value still shows, wait a few seconds and read it again, because the endpoint answers from the new kubelet only after it has started.

## Common pitfalls

> [!WARNING]
> Editing only `config.yaml` changes nothing when a flag overrides the value. Removing the whole `KUBELET_KUBEADM_ARGS` line also removes the container runtime endpoint and the node IP, and the kubelet fails. Check the effective value with `configz`, not the file.
