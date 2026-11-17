---
exam_objectives:
- Use CIS benchmark to review the security configuration of Kubernetes components
  (etcd, kubelet, kubedns, kubeapi)
---
# Harden The Controller Manager And Scheduler

Allow about 12 minutes for the tasks.

A benchmark run on the `starfleet` control plane lists failures for the controller manager, the scheduler and the manifest files. Close these findings.

## Starting state

The kind cluster has one control plane node and one worker node. The `starfleet-031-020-03-06` namespace runs two `probe` replicas behind the `probe` Service and a `shuttle` client pod. The controller manager and the scheduler run with the profiling endpoint on (the default). Some files in `/etc/kubernetes/manifests` have mode `644`.

Connect to this lab from a host shell. The command `astrona kubeconfig` prints the path of the lab's kubeconfig, the file that tells `kubectl` which cluster to use and which credentials to send. The two variables hold the names of the node containers: `node_name` is the control plane node and `worker_name` is the worker node.

```sh
export KUBECONFIG="$(astrona kubeconfig ats-031-lab-020-03-06)"
test "$(kubectl config current-context)" = "kind-astro-ats-031-lab-020-03-06" || exit 1
node_name="astro-ats-031-lab-020-03-06-control-plane"
worker_name="astro-ats-031-lab-020-03-06-worker"
```

Run node commands as `podman exec "$node_name" ...` or `podman exec "$worker_name" ...`. They change only the node containers of this lab, not your own computer.

## Required result

- The kube-controller-manager and the kube-scheduler on the control plane node run with `--profiling=false`.
- Every file in `/etc/kubernetes/manifests` has mode `600` or stricter and the owner `root:root`.
- Both pods are running and ready, the API server stays ready and both `probe` replicas stay available.

## Verify The Result

The grader reads the command lines of the running `kube-controller-manager` and `kube-scheduler` processes and runs `stat` on every manifest.
