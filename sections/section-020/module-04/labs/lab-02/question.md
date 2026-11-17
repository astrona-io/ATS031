---
exam_objectives:
- Use CIS benchmark to review the security configuration of Kubernetes components
  (etcd, kubelet, kubedns, kubeapi)
---
# Record How The API Server Connects To etcd

Allow about 8 minutes for the tasks.

Before a review of the `starfleet` control plane, the security team wants to know exactly how the API server reaches etcd and which files prove its identity.

## Starting state

The kind cluster has one control plane node and one worker node. The `starfleet-031-020-04-02` namespace runs two `probe` replicas behind the `probe` Service and a `shuttle` client pod. etcd runs as a static pod on the control plane node.

Connect to this lab from a host shell. The command `astrona kubeconfig` prints the path of the lab's kubeconfig, the file that tells `kubectl` which cluster to use and which credentials to send. The two variables hold the names of the node containers: `node_name` is the control plane node and `worker_name` is the worker node.

```sh
export KUBECONFIG="$(astrona kubeconfig ats-031-lab-020-04-02)"
test "$(kubectl config current-context)" = "kind-astro-ats-031-lab-020-04-02" || exit 1
node_name="astro-ats-031-lab-020-04-02-control-plane"
worker_name="astro-ats-031-lab-020-04-02-worker"
```

Run node commands as `podman exec "$node_name" ...` or `podman exec "$worker_name" ...`. They change only the node containers of this lab, not your own computer.

## Required result

Create the ConfigMap `etcd-connection` in the `starfleet-031-020-04-02` namespace with these keys. Read each value from the running API server, not from memory:

- `servers`: the value of `--etcd-servers`.
- `client-certificate`: the path in `--etcd-certfile`.
- `client-key`: the path in `--etcd-keyfile`.
- `ca-file`: the path in `--etcd-cafile`.

Do not change the cluster.

## Verify The Result

The grader reads the command line of the running `kube-apiserver` process on the control plane node and compares each flag with your ConfigMap.
