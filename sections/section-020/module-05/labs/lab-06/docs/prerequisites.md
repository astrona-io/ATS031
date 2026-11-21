---
exam_objectives:
- Use CIS benchmark to review the security configuration of Kubernetes components
  (etcd, kubelet, kubedns, kubeapi)
---
# Prerequisites

Use astrona, kubectl and a shell. Every step uses `kubectl` from your own computer; no step runs a command on a node.

Connect to this lab from a host shell. The command `astrona kubeconfig` prints the path of the lab's kubeconfig, the file that tells `kubectl` which cluster to use and which credentials to send. The `test` line stops the shell when `kubectl` points at another cluster.

```sh
export KUBECONFIG="$(astrona kubeconfig ats-031-lab-020-05-06)"
test "$(kubectl config current-context)" = "kind-astro-ats-031-lab-020-05-06" || exit 1
```

Every step of this lab uses `kubectl` only. No step runs a command on a node.
