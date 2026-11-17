---
exam_objectives:
- Use CIS benchmark to review the security configuration of Kubernetes components
  (etcd, kubelet, kubedns, kubeapi)
---
# Audit The Worker Node With A kube-bench Job

Allow about 10 minutes for the tasks.

The `starfleet` cluster has a control plane report, but nobody has audited the worker node yet. Run the worker audit.

## Starting state

The kind cluster has one control plane node and one worker node. The `starfleet-031-020-02-03` namespace runs two `probe` replicas behind the `probe` Service and a `shuttle` client pod. The `kube-bench` image `docker.io/aquasec/kube-bench:v0.10.6` is already loaded on both nodes. No kube-bench Job exists.

Connect to this lab from a host shell. The command `astrona kubeconfig` prints the path of the lab's kubeconfig, the file that tells `kubectl` which cluster to use and which credentials to send. The two variables hold the names of the node containers: `node_name` is the control plane node and `worker_name` is the worker node.

```sh
export KUBECONFIG="$(astrona kubeconfig ats-031-lab-020-02-03)"
test "$(kubectl config current-context)" = "kind-astro-ats-031-lab-020-02-03" || exit 1
node_name="astro-ats-031-lab-020-02-03-control-plane"
worker_name="astro-ats-031-lab-020-02-03-worker"
```

Run node commands as `podman exec "$node_name" ...` or `podman exec "$worker_name" ...`. They change only the node containers of this lab, not your own computer.

## Required result

- Create the Job `node-audit` in the `starfleet-031-020-02-03` namespace. It runs `kube-bench run --targets node` with the image `docker.io/aquasec/kube-bench:v0.10.6`.
- The pod runs on the worker node `astro-ats-031-lab-020-02-03-worker`, shares the process namespace of the node (`hostPID: true`) and mounts the node directories that the audit reads.
- The Job completes, and its log holds the results of the worker node section of the benchmark.

## Verify The Result

The grader reads the Job, the node of its pod and the log of the pod. A log without worker node results fails, for example when the pod could not read the kubelet process.
