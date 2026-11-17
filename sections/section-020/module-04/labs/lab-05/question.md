---
exam_objectives:
- Use CIS benchmark to review the security configuration of Kubernetes components
  (etcd, kubelet, kubedns, kubeapi)
---
# Find A Secret Directly In etcd

Allow about 10 minutes for the tasks.

A Secret called `relay-token` exists somewhere in the `starfleet` cluster. The security team wants to see where etcd stores it, without asking the API server.

## Starting state

The kind cluster has one control plane node and one worker node. The `starfleet-031-020-04-05` namespace runs two `probe` replicas behind the `probe` Service and a `shuttle` client pod. etcd runs as a static pod on the control plane node. A Secret called `relay-token` exists in one namespace of the cluster. The lab does not tell you which namespace.

Connect to this lab from a host shell. The command `astrona kubeconfig` prints the path of the lab's kubeconfig, the file that tells `kubectl` which cluster to use and which credentials to send. The two variables hold the names of the node containers: `node_name` is the control plane node and `worker_name` is the worker node.

```sh
export KUBECONFIG="$(astrona kubeconfig ats-031-lab-020-04-05)"
test "$(kubectl config current-context)" = "kind-astro-ats-031-lab-020-04-05" || exit 1
node_name="astro-ats-031-lab-020-04-05-control-plane"
worker_name="astro-ats-031-lab-020-04-05-worker"
```

Run node commands as `podman exec "$node_name" ...` or `podman exec "$worker_name" ...`. They change only the node containers of this lab, not your own computer.

## Required result

Use `etcdctl` against etcd, not `kubectl get secret`, to find the Secret. Then create the ConfigMap `etcd-query` in the `starfleet-031-020-04-05` namespace with these keys:

- `secret-key`: the full etcd key of the Secret `relay-token`, for example `/registry/secrets/<namespace>/relay-token`.
- `secret-namespace`: the namespace that the key names.
- `member-name`: the name of the etcd member, as `etcdctl member list` prints it.

## Verify The Result

The grader asks the API server where `relay-token` is and reads the `--name` flag of the running `etcd` process.
