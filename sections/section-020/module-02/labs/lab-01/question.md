---
exam_objectives:
- Use CIS benchmark to review the security configuration of Kubernetes components
  (etcd, kubelet, kubedns, kubeapi)
---
# Save The Failing API Server Check Ids

Allow about 12 minutes for the tasks.

The security team of the `starfleet` cluster needs the list of failing API server checks in a form that a script can read, before it plans fixes.

## Starting state

The kind cluster has one control plane node and one worker node. The `starfleet-031-020-02-01` namespace runs two `probe` replicas behind the `probe` Service and a `shuttle` client pod. The `kube-bench` image `docker.io/aquasec/kube-bench:v0.10.6` is already loaded on both nodes. The control plane node runs with the kubeadm defaults. No kube-bench result has been collected.

Connect to this lab from a host shell. The command `astrona kubeconfig` prints the path of the lab's kubeconfig, the file that tells `kubectl` which cluster to use and which credentials to send. The two variables hold the names of the node containers: `node_name` is the control plane node and `worker_name` is the worker node.

```sh
export KUBECONFIG="$(astrona kubeconfig ats-031-lab-020-02-01)"
test "$(kubectl config current-context)" = "kind-astro-ats-031-lab-020-02-01" || exit 1
node_name="astro-ats-031-lab-020-02-01-control-plane"
worker_name="astro-ats-031-lab-020-02-01-worker"
```

Run node commands as `podman exec "$node_name" ...` or `podman exec "$worker_name" ...`. They change only the node containers of this lab, not your own computer.

## Required result

- Create the Job `api-server-audit` in the `starfleet-031-020-02-01` namespace. It runs `kube-bench run --targets master --json` on the control plane node and completes.
- From its JSON output, find every check with the status `FAIL` whose number starts with `1.2.`.
- Create the ConfigMap `failing-checks` in the same namespace with the numbers under the key `ids`, one number on each line.

Do not change any setting of the cluster. The grader runs kube-bench again and compares its failing `1.2.` checks with your list.

## Verify The Result

The grader reads your Job, then runs its own JSON audit in the same namespace and compares the result with your ConfigMap. A list that is too short, too long, or that holds a number outside `1.2.` fails.
