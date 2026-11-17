---
exam_objectives:
- Use CIS benchmark to review the security configuration of Kubernetes components
  (etcd, kubelet, kubedns, kubeapi)
---
# Prerequisites

Use astrona, kubectl and a shell with Podman. Node commands run inside the node containers of this lab, not on your own computer.

Connect to this lab from a host shell. The command `astrona kubeconfig` prints the path of the lab's kubeconfig, the file that tells `kubectl` which cluster to use and which credentials to send. The two variables hold the names of the node containers: `node_name` is the control plane node and `worker_name` is the worker node.

```sh
export KUBECONFIG="$(astrona kubeconfig ats-031-lab-020-02-04)"
test "$(kubectl config current-context)" = "kind-astro-ats-031-lab-020-02-04" || exit 1
node_name="astro-ats-031-lab-020-02-04-control-plane"
worker_name="astro-ats-031-lab-020-02-04-worker"
```

Run node commands as `podman exec "$node_name" ...` or `podman exec "$worker_name" ...`. They change only the node containers of this lab, not your own computer.
