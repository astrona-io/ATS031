---
exam_objectives:
- Use CIS benchmark to review the security configuration of Kubernetes components
  (etcd, kubelet, kubedns, kubeapi)
---
# Restrict Control Plane Kubeconfig And Key Files

Allow about 8 minutes for the tasks.

A file scan of the `starfleet` control plane node reports that some credential files can be read by every local user. Find them and close them.

## Starting state

The kind cluster has one control plane node and one worker node. The `starfleet-031-020-01-02` namespace runs two `probe` replicas behind the `probe` Service and a `shuttle` client pod. Some files in `/etc/kubernetes` and `/etc/kubernetes/pki` on the control plane node have mode `644`. The lab does not tell you which ones.

Connect to this lab from a host shell. The command `astrona kubeconfig` prints the path of the lab's kubeconfig, the file that tells `kubectl` which cluster to use and which credentials to send. The two variables hold the names of the node containers: `node_name` is the control plane node and `worker_name` is the worker node.

```sh
export KUBECONFIG="$(astrona kubeconfig ats-031-lab-020-01-02)"
test "$(kubectl config current-context)" = "kind-astro-ats-031-lab-020-01-02" || exit 1
node_name="astro-ats-031-lab-020-01-02-control-plane"
worker_name="astro-ats-031-lab-020-01-02-worker"
```

Run node commands as `podman exec "$node_name" ...` or `podman exec "$worker_name" ...`. They change only the node containers of this lab, not your own computer.

## Required result

- Every kubeconfig file `/etc/kubernetes/*.conf` on the control plane node has mode `600` or stricter and the owner `root:root`.
- Every private key file (`*.key`) under `/etc/kubernetes/pki` on the control plane node has mode `600` or stricter and the owner `root:root`.
- The API server stays ready and both `probe` replicas stay available.

Do not change certificate files (`*.crt`); the benchmark allows mode `644` for them.

## Verify The Result

The grader runs `stat` on every matching file on the control plane node. A mode such as `400` also passes, because it is stricter than `600`.
