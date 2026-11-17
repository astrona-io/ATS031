---
exam_objectives:
- Use CIS benchmark to review the security configuration of Kubernetes components
  (etcd, kubelet, kubedns, kubeapi)
---
# Record The Totals Of A kube-bench Report

Allow about 10 minutes for the tasks.

The `starfleet` platform team tracks its benchmark progress in numbers. Run the control plane audit and record the numbers of this run.

## Starting state

The kind cluster has one control plane node and one worker node. The `starfleet-031-020-02-05` namespace runs two `probe` replicas behind the `probe` Service and a `shuttle` client pod. The `kube-bench` image `docker.io/aquasec/kube-bench:v0.10.6` is already loaded on both nodes. No kube-bench Job exists.

Connect to this lab from a host shell. The command `astrona kubeconfig` prints the path of the lab's kubeconfig, the file that tells `kubectl` which cluster to use and which credentials to send. The two variables hold the names of the node containers: `node_name` is the control plane node and `worker_name` is the worker node.

```sh
export KUBECONFIG="$(astrona kubeconfig ats-031-lab-020-02-05)"
test "$(kubectl config current-context)" = "kind-astro-ats-031-lab-020-02-05" || exit 1
node_name="astro-ats-031-lab-020-02-05-control-plane"
worker_name="astro-ats-031-lab-020-02-05-worker"
```

Run node commands as `podman exec "$node_name" ...` or `podman exec "$worker_name" ...`. They change only the node containers of this lab, not your own computer.

## Required result

- Create the Job `master-audit` in the `starfleet-031-020-02-05` namespace. It runs `kube-bench run --targets master` on the control plane node and completes.
- Create the ConfigMap `master-result` in the same namespace with these keys, all read from the log of `master-audit`:
  - `pass`, `fail`, `warn` and `info`: the totals in the summary at the end of the log.
  - `fail-1.1`: the number of `[FAIL]` lines for checks in section `1.1` (control plane node configuration files).
  - `fail-1.2`: the number of `[FAIL]` lines for checks in section `1.2` (API server).

## Verify The Result

The grader reads the log of your finished `master-audit` pod and compares its summary and its `[FAIL]` lines with your ConfigMap. Do not change the cluster after the run.
