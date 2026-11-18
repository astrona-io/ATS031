---
exam_objectives:
- Use CIS benchmark to review the security configuration of Kubernetes components
  (etcd, kubelet, kubedns, kubeapi)
---
# Restrict The etcd Data Directory

Allow about 8 minutes for the tasks.

A benchmark report for the `starfleet` cluster lists a finding for the etcd data directory. Fix it and record the facts for the report.

## Starting state

The lab VM runs a one-node Kubernetes cluster built with kubeadm, the standard tool that installs a cluster on a Linux machine. The node `astro-ats-031-lab-020-04-04` is the control plane and also runs the pods. The `starfleet-031-020-04-04` namespace runs two `probe` replicas behind the `probe` Service and a `shuttle` client pod. etcd runs as a static pod on the control plane node. Someone opened the mode of the etcd data directory.

Open a shell on the lab VM (virtual machine) and check that kubectl uses this lab's cluster:

```sh
astrona ssh astro-ats-031-lab-020-04-04
kubectl config current-context
```

The second command prints `kubernetes-admin@astro-ats-031-lab-020-04-04`. You are logged in as the `student` user, which has a kubeconfig file for the cluster. A kubeconfig file tells `kubectl` which cluster to use and which credentials to send. Node files and processes belong to root, so run node commands with `sudo`. They change only the lab VM, not your own computer.

## Required result

- The directory that etcd uses for its data (the value of its `--data-dir` flag) has mode `700` or stricter and the owner `root:root`.
- Create the ConfigMap `etcd-process` in the `starfleet-031-020-04-04` namespace with two keys: `data-dir`, the value of `--data-dir` of the running etcd process, and `user`, the user that runs that process.
- etcd stays healthy: `kubectl get --raw=/readyz/etcd` prints `ok`.

## Verify The Result

The grader reads the command line and the user of the running `etcd` process and the mode of the data directory on the control plane node.
