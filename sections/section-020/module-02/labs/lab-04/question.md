---
exam_objectives:
- Use CIS benchmark to review the security configuration of Kubernetes components
  (etcd, kubelet, kubedns, kubeapi)
---
# Run The etcd Checks With A Pinned Benchmark Edition

Allow about 10 minutes for the tasks.

The etcd team of the `starfleet` cluster must report against one fixed benchmark edition, not the one that kube-bench detects. Run their audit.

## Starting state

The kind cluster has one control plane node and one worker node. The `starfleet-031-020-02-04` namespace runs two `probe` replicas behind the `probe` Service and a `shuttle` client pod. The `kube-bench` image `docker.io/aquasec/kube-bench:v0.10.6` is already loaded on both nodes. The ConfigMap `audit-request` in the `starfleet-031-020-02-04` namespace names the benchmark edition under the key `benchmark`. No kube-bench Job exists.

Connect to this lab from a host shell. The command `astrona kubeconfig` prints the path of the lab's kubeconfig, the file that tells `kubectl` which cluster to use and which credentials to send. The two variables hold the names of the node containers: `node_name` is the control plane node and `worker_name` is the worker node.

```sh
export KUBECONFIG="$(astrona kubeconfig ats-031-lab-020-02-04)"
test "$(kubectl config current-context)" = "kind-astro-ats-031-lab-020-02-04" || exit 1
node_name="astro-ats-031-lab-020-02-04-control-plane"
worker_name="astro-ats-031-lab-020-02-04-worker"
```

Run node commands as `podman exec "$node_name" ...` or `podman exec "$worker_name" ...`. They change only the node containers of this lab, not your own computer.

## Required result

- Create the Job `etcd-audit` in the `starfleet-031-020-02-04` namespace. It runs kube-bench on the control plane node with the target `etcd` only and with `--benchmark` set to the edition in `audit-request`.
- The Job completes, and its log holds the etcd checks (section `2`) and no control plane checks (section `1`).

## Verify The Result

The grader reads the command of the Job and the log of its finished pod.
