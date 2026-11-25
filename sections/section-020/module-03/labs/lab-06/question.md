---
exam_objectives:
- Use CIS benchmark to review the security configuration of Kubernetes components
  (etcd, kubelet, kubedns, kubeapi)
---
# Harden The Controller Manager And Scheduler

Allow about 12 minutes for the tasks.

A benchmark run on the `starfleet` control plane lists failures for the controller manager, the scheduler and the manifest files. Close these findings.

## Starting state

The lab VM runs a one-node Kubernetes cluster built with kubeadm, the standard tool that installs a cluster on a Linux machine. The node `astro-ats-031-lab-020-03-06` is the control plane and also runs the pods. The `starfleet-031-020-03-06` namespace runs two `probe` replicas behind the `probe` Service and a `shuttle` client pod. The controller manager and the scheduler run with the profiling endpoint on (the default). Some files in `/etc/kubernetes/manifests` have mode `644`.

Open a shell on the lab VM (virtual machine) and check that kubectl uses this lab's cluster:

```sh
astrona ssh astro-ats-031-lab-020-03-06
kubectl config current-context
```

The second command prints `kubernetes-admin@astro-ats-031-lab-020-03-06`. You are logged in as the `student` user, which has a kubeconfig file for the cluster. A kubeconfig file tells `kubectl` which cluster to use and which credentials to send. Node files and processes belong to root, so run node commands with `sudo`. They change only the lab VM, not your own computer.

## Required result

- The kube-controller-manager and the kube-scheduler on the control plane node run with `--profiling=false`.
- Every file in `/etc/kubernetes/manifests` has mode `600` or stricter and the owner `root:root`.
- Both pods are running and ready, the API server stays ready and both `probe` replicas stay available.

## Verify The Result

The grader reads the command lines of the running `kube-controller-manager` and `kube-scheduler` processes and runs `stat` on every manifest.
