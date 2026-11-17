---
exam_objectives:
- Use CIS benchmark to review the security configuration of Kubernetes components
  (etcd, kubelet, kubedns, kubeapi)
---
# Remove A Kubelet Flag That Overrides The Configuration File

Allow about 10 minutes for the tasks.

The kubelet configuration file on the `starfleet` worker node says `Webhook`, but a scan reports that the kubelet allows every request. Find the source of the real value and fix it.

## Starting state

The kind cluster has one control plane node and one worker node. The `starfleet-031-020-05-03` namespace runs two `probe` replicas behind the `probe` Service and a `shuttle` client pod. The file `/var/lib/kubelet/config.yaml` on the worker node sets `authorization.mode: Webhook`. A copy of the kubelet files is in `/opt/training/backup` on the worker node.

Connect to this lab from a host shell. The command `astrona kubeconfig` prints the path of the lab's kubeconfig, the file that tells `kubectl` which cluster to use and which credentials to send. The two variables hold the names of the node containers: `node_name` is the control plane node and `worker_name` is the worker node.

```sh
export KUBECONFIG="$(astrona kubeconfig ats-031-lab-020-05-03)"
test "$(kubectl config current-context)" = "kind-astro-ats-031-lab-020-05-03" || exit 1
node_name="astro-ats-031-lab-020-05-03-control-plane"
worker_name="astro-ats-031-lab-020-05-03-worker"
```

Run node commands as `podman exec "$node_name" ...` or `podman exec "$worker_name" ...`. They change only the node containers of this lab, not your own computer.

## Required result

- The effective configuration of the kubelet on the worker node `astro-ats-031-lab-020-05-03-worker` has `authorization.mode` set to `Webhook`.
- No kubelet source sets the authorization mode on the command line: neither `/var/lib/kubelet/kubeadm-flags.env` nor the running kubelet process has an `--authorization-mode` flag.
- The worker node is `Ready`, and both `probe` replicas stay available.

## Verify The Result

The grader reads the flags file and the command line of the running `kubelet` process on the worker node, and the effective configuration through the `configz` endpoint of the API server.
