---
exam_objectives:
- Use CIS benchmark to review the security configuration of Kubernetes components
  (etcd, kubelet, kubedns, kubeapi)
---
# Correct The Scheduler Bind Address And Record It

Allow about 10 minutes for the tasks.

A benchmark run on the `starfleet` control plane reports that the scheduler accepts connections on every address of the node. Correct the finding and record it for the review.

## Starting state

The kind cluster has one control plane node and one worker node. The `starfleet-031-020-01-01` namespace runs two `probe` replicas behind the `probe` Service and a `shuttle` client pod. The kube-scheduler static pod runs with `--bind-address=0.0.0.0`, so its secure port `10259` listens on every address of the control plane node.

Connect to this lab from a host shell. The command `astrona kubeconfig` prints the path of the lab's kubeconfig, the file that tells `kubectl` which cluster to use and which credentials to send. The two variables hold the names of the node containers: `node_name` is the control plane node and `worker_name` is the worker node.

```sh
export KUBECONFIG="$(astrona kubeconfig ats-031-lab-020-01-01)"
test "$(kubectl config current-context)" = "kind-astro-ats-031-lab-020-01-01" || exit 1
node_name="astro-ats-031-lab-020-01-01-control-plane"
worker_name="astro-ats-031-lab-020-01-01-worker"
```

Run node commands as `podman exec "$node_name" ...` or `podman exec "$worker_name" ...`. They change only the node containers of this lab, not your own computer.

## Required result

- The kube-scheduler on the control plane node runs with `--bind-address=127.0.0.1`, so its port `10259` answers only on `127.0.0.1`.
- Keep any backup of the manifest outside `/etc/kubernetes/manifests`.
- Create the ConfigMap `benchmark-review` in the `starfleet-031-020-01-01` namespace with `component: kube-scheduler`, `check: 1.4.2`, `setting: bind-address` and `result: corrected`.
- The kube-scheduler pod is running again, the API server stays ready and both `probe` replicas stay available.

## Verify The Result

The grader reads the command line of the running `kube-scheduler` process, not only the manifest, and connects to port `10259` on the loopback address and on the node address. It also reads the ConfigMap.
