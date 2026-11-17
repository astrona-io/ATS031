---
exam_objectives:
- Use CIS benchmark to review the security configuration of Kubernetes components
  (etcd, kubelet, kubedns, kubeapi)
---
# Enable NodeRestriction

Allow about 10 minutes for the tasks.

The security team of the `starfleet` cluster asks what an attacker could do with the credentials of one worker node. Today the answer is: put any label on its own node, even the labels that should steer sensitive pods. Limit what a kubelet may write.

## Starting state

The kind cluster has one control plane node and one worker node. The `starfleet-031-020-03-05` namespace runs two `probe` replicas behind the `probe` Service and a `shuttle` client pod. The API server runs without the `NodeRestriction` admission plugin.

Connect to this lab from a host shell. The command `astrona kubeconfig` prints the path of the lab's kubeconfig, the file that tells `kubectl` which cluster to use and which credentials to send. The two variables hold the names of the node containers: `node_name` is the control plane node and `worker_name` is the worker node.

```sh
export KUBECONFIG="$(astrona kubeconfig ats-031-lab-020-03-05)"
test "$(kubectl config current-context)" = "kind-astro-ats-031-lab-020-03-05" || exit 1
node_name="astro-ats-031-lab-020-03-05-control-plane"
worker_name="astro-ats-031-lab-020-03-05-worker"
```

Run node commands as `podman exec "$node_name" ...` or `podman exec "$worker_name" ...`. They change only the node containers of this lab, not your own computer.

## Required result

- The API server on the control plane node runs with `NodeRestriction` in `--enable-admission-plugins`, and the plugin is not in `--disable-admission-plugins`.
- The kubelet credentials of the worker node (`/etc/kubernetes/kubelet.conf` on the worker) can no longer add a label with the prefix `node-restriction.kubernetes.io/` to the worker node.
- Keep the other admission plugins that the API server uses now.
- The API server stays ready and both `probe` replicas stay available.

## Verify The Result

The grader reads the command line of the running `kube-apiserver` process. It then runs `kubectl` on the worker node with the kubelet kubeconfig and tries to add the label `node-restriction.kubernetes.io/lab-check=kubelet` to the worker node. It removes the label again if the request succeeds.
