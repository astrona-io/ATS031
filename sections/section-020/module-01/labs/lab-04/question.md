---
exam_objectives:
- Use CIS benchmark to review the security configuration of Kubernetes components
  (etcd, kubelet, kubedns, kubeapi)
---
# Report The Effective Kubelet Settings

Allow about 10 minutes for the tasks.

A colleague reviewed only the kubelet configuration file of the `starfleet` worker node and reported that everything is closed. Check what the kubelet really runs with.

## Starting state

The kind cluster has one control plane node and one worker node. The `starfleet-031-020-01-04` namespace runs two `probe` replicas behind the `probe` Service and a `shuttle` client pod. The kubelet on the worker node runs with a setting that is not in its configuration file. The file `/var/lib/kubelet/config.yaml` on the worker has mode `644`.

Connect to this lab from a host shell. The command `astrona kubeconfig` prints the path of the lab's kubeconfig, the file that tells `kubectl` which cluster to use and which credentials to send. The two variables hold the names of the node containers: `node_name` is the control plane node and `worker_name` is the worker node.

```sh
export KUBECONFIG="$(astrona kubeconfig ats-031-lab-020-01-04)"
test "$(kubectl config current-context)" = "kind-astro-ats-031-lab-020-01-04" || exit 1
node_name="astro-ats-031-lab-020-01-04-control-plane"
worker_name="astro-ats-031-lab-020-01-04-worker"
```

Run node commands as `podman exec "$node_name" ...` or `podman exec "$worker_name" ...`. They change only the node containers of this lab, not your own computer.

## Required result

- Create the ConfigMap `kubelet-review` in the `starfleet-031-020-01-04` namespace with three keys that hold the **effective** values of the kubelet on the worker node:
  - `anonymous-enabled`: `true` or `false`, from `authentication.anonymous.enabled`.
  - `authorization-mode`: the value of `authorization.mode`, for example `Webhook`.
  - `read-only-port`: the number in `readOnlyPort`, for example `0`.
- Set the mode of `/var/lib/kubelet/config.yaml` on the worker node to `600` or stricter, with the owner `root:root`.
- Do not change any other kubelet setting. The worker node stays `Ready`.

## Verify The Result

The grader reads the effective kubelet configuration of the worker node through the API server (`configz`) and compares it with your ConfigMap. It also runs `stat` on the configuration file.
