---
exam_objectives:
- Use CIS benchmark to review the security configuration of Kubernetes components
  (etcd, kubelet, kubedns, kubeapi)
---
# Report The Effective Kubelet Settings Solution

Open a shell on the lab VM (virtual machine) and check that kubectl uses this lab's cluster:

```sh
astrona ssh astro-ats-031-lab-020-01-04
kubectl config current-context
```

The second command prints `kubernetes-admin@astro-ats-031-lab-020-01-04`. You are logged in as the `student` user, which has a kubeconfig file for the cluster. A kubeconfig file tells `kubectl` which cluster to use and which credentials to send. Node files and processes belong to root, so run node commands with `sudo`. They change only the lab VM, not your own computer.

## Read the effective values

The kubelet takes its settings from three places: its defaults, the file `/var/lib/kubelet/config.yaml`, and command-line flags. A flag overrides the file. The API server can proxy a request to the kubelet and return the merged result at the path `configz`. Read the three values from it:

```sh
kubectl get --raw "/api/v1/nodes/astro-ats-031-lab-020-01-04/proxy/configz" | python3 -m json.tool | grep -A2 -e '"anonymous"' -e '"authorization"' -e '"readOnlyPort"'
```

The output shows `"readOnlyPort": 10255`, but the configuration file does not set this field. Check the file and the flags file on the node to see where the value comes from:

```sh
sudo grep -i readonly /var/lib/kubelet/config.yaml
sudo cat /var/lib/kubelet/kubeadm-flags.env
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
sudo chmod 600 /var/lib/kubelet/config.yaml
sudo stat -c '%a %U:%G %n' /var/lib/kubelet/config.yaml
kubectl get node "astro-ats-031-lab-020-01-04"
```

The `stat` line starts with `600 root:root`, and the node stays `Ready`.

## Common pitfalls

> [!WARNING]
> Reading only `config.yaml` misses flags such as `--read-only-port` in `kubeadm-flags.env`. `configz` returns `readOnlyPort` only when it is not zero, so a missing field means `0`. Do not restart the kubelet with a broken file; check the file before every restart.
