---
exam_objectives:
- Use CIS benchmark to review the security configuration of Kubernetes components
  (etcd, kubelet, kubedns, kubeapi)
---
# Restrict The etcd Data Directory

Allow about 8 minutes for the tasks.

A benchmark report for the `starfleet` cluster lists a finding for the etcd data directory. Fix it and record the facts for the report.

## Starting state

The kind cluster has one control plane node and one worker node. The `starfleet-031-020-04-04` namespace runs two `probe` replicas behind the `probe` Service and a `shuttle` client pod. etcd runs as a static pod on the control plane node. Someone opened the mode of the etcd data directory.

Connect to this lab from a host shell. The command `astrona kubeconfig` prints the path of the lab's kubeconfig, the file that tells `kubectl` which cluster to use and which credentials to send. The two variables hold the names of the node containers: `node_name` is the control plane node and `worker_name` is the worker node.

```sh
export KUBECONFIG="$(astrona kubeconfig ats-031-lab-020-04-04)"
test "$(kubectl config current-context)" = "kind-astro-ats-031-lab-020-04-04" || exit 1
node_name="astro-ats-031-lab-020-04-04-control-plane"
worker_name="astro-ats-031-lab-020-04-04-worker"
```

Run node commands as `podman exec "$node_name" ...` or `podman exec "$worker_name" ...`. They change only the node containers of this lab, not your own computer.

## Required result

- The directory that etcd uses for its data (the value of its `--data-dir` flag) has mode `700` or stricter and the owner `root:root`.
- Create the ConfigMap `etcd-process` in the `starfleet-031-020-04-04` namespace with two keys: `data-dir`, the value of `--data-dir` of the running etcd process, and `user`, the user that runs that process.
- etcd stays healthy: `kubectl get --raw=/readyz/etcd` prints `ok`.

## Verify The Result

The grader reads the command line and the user of the running `etcd` process and the mode of the data directory on the control plane node.
