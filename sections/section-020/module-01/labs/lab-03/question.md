---
exam_objectives:
- Use CIS benchmark to review the security configuration of Kubernetes components
  (etcd, kubelet, kubedns, kubeapi)
---
# Record A Manual Audit Of The API Server And etcd

Allow about 10 minutes for the tasks.

The auditor of the `starfleet` cluster does not trust a report that only copies default values. Read the real values from the running control plane and record them.

## Starting state

The kind cluster has one control plane node and one worker node. The `starfleet-031-020-01-03` namespace runs two `probe` replicas behind the `probe` Service and a `shuttle` client pod. The API server and etcd run with settings that this lab chose at start. Some differ from the kubeadm defaults, and the lab does not tell you which.

Connect to this lab from a host shell. The command `astrona kubeconfig` prints the path of the lab's kubeconfig, the file that tells `kubectl` which cluster to use and which credentials to send. The two variables hold the names of the node containers: `node_name` is the control plane node and `worker_name` is the worker node.

```sh
export KUBECONFIG="$(astrona kubeconfig ats-031-lab-020-01-03)"
test "$(kubectl config current-context)" = "kind-astro-ats-031-lab-020-01-03" || exit 1
node_name="astro-ats-031-lab-020-01-03-control-plane"
worker_name="astro-ats-031-lab-020-01-03-worker"
```

Run node commands as `podman exec "$node_name" ...` or `podman exec "$worker_name" ...`. They change only the node containers of this lab, not your own computer.

## Required result

Create the ConfigMap `manual-audit` in the `starfleet-031-020-01-03` namespace with these four keys. Each value must be the value that the running component or the node uses now:

- `apiserver-authorization-mode`: the value of the API server flag `--authorization-mode`, as written in the flag (for example `Node,RBAC`).
- `apiserver-profiling`: `true` or `false`, the effective profiling setting of the API server. When the flag is not set, the default applies.
- `etcd-client-cert-auth`: `true` or `false`, the effective value of the etcd flag `--client-cert-auth`.
- `etcd-data-dir-mode`: the octal mode of the etcd data directory `/var/lib/etcd` on the control plane node, as `stat -c %a` prints it (for example `700`).

Do not change any setting of the cluster.

## Verify The Result

The grader reads the command line of the running `kube-apiserver` and `etcd` processes and the mode of `/var/lib/etcd`, and compares them with your ConfigMap. A value copied from documentation or from a default fails when the lab chose a different value.
