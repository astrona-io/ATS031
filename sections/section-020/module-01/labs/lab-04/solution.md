---
exam_objectives:
- Use CIS benchmark to review the security configuration of Kubernetes components
  (etcd, kubelet, kubedns, kubeapi)
---
# Report The Effective Kubelet Settings Solution

Connect to this lab from a host shell. The command `astrona kubeconfig` prints the path of the lab's kubeconfig, the file that tells `kubectl` which cluster to use and which credentials to send. The two variables hold the names of the node containers: `node_name` is the control plane node and `worker_name` is the worker node.

```sh
export KUBECONFIG="$(astrona kubeconfig ats-031-lab-020-01-04)"
test "$(kubectl config current-context)" = "kind-astro-ats-031-lab-020-01-04" || exit 1
node_name="astro-ats-031-lab-020-01-04-control-plane"
worker_name="astro-ats-031-lab-020-01-04-worker"
```

Run node commands as `podman exec "$node_name" ...` or `podman exec "$worker_name" ...`. They change only the node containers of this lab, not your own computer.

## Read the effective values

The kubelet takes its settings from three places: its defaults, the file `/var/lib/kubelet/config.yaml`, and command-line flags. A flag overrides the file. The API server can proxy a request to the kubelet and return the merged result at the path `configz`. Read the three values from it:

```sh
kubectl get --raw "/api/v1/nodes/$worker_name/proxy/configz" | python3 -m json.tool | grep -A2 -e '"anonymous"' -e '"authorization"' -e '"readOnlyPort"'
```

The output shows `"readOnlyPort": 10255`, but the configuration file does not set this field. Check the file and the flags file on the worker to see where the value comes from:

```sh
podman exec "$worker_name" grep -i readonly /var/lib/kubelet/config.yaml
podman exec "$worker_name" cat /var/lib/kubelet/kubeadm-flags.env
```

The first command prints nothing. The second shows `--read-only-port=10255` in `KUBELET_KUBEADM_ARGS`. This flag is the override that the file review missed. The task asks you to report it, not to remove it.

## Record the result and restrict the file

Save this as `configmap-kubelet-review.yaml`. Use the values you read from `configz`; quote them so that they stay strings:

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: kubelet-review
  namespace: starfleet-031-020-01-04
data:
  anonymous-enabled: "<true-or-false>"
  authorization-mode: "<MODE>"
  read-only-port: "<PORT>"
```

Apply it:

```sh
kubectl apply -f configmap-kubelet-review.yaml
```

The kubelet reads its configuration file when it starts, so a mode change needs no restart. Restrict the file and check it:

```sh
podman exec "$worker_name" chmod 600 /var/lib/kubelet/config.yaml
podman exec "$worker_name" stat -c '%a %U:%G %n' /var/lib/kubelet/config.yaml
kubectl get node "$worker_name"
```

The `stat` line starts with `600 root:root`, and the node stays `Ready`.

## Common pitfalls

> [!WARNING]
> Reading only `config.yaml` misses flags such as `--read-only-port` in `kubeadm-flags.env`. `configz` returns `readOnlyPort` only when it is not zero, so a missing field means `0`. Do not restart the kubelet with a broken file; check the file before every restart.
