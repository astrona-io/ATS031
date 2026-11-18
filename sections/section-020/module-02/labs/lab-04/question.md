---
exam_objectives:
- Use CIS benchmark to review the security configuration of Kubernetes components
  (etcd, kubelet, kubedns, kubeapi)
---
# Run The etcd Checks With A Pinned Benchmark Edition

Allow about 10 minutes for the tasks.

The etcd team of the `starfleet` cluster must report against one fixed benchmark edition, not the one that kube-bench detects. Run their audit.

## Starting state

The lab VM runs a one-node Kubernetes cluster built with kubeadm, the standard tool that installs a cluster on a Linux machine. The node `astro-ats-031-lab-020-02-04` is the control plane and also runs the pods. The `starfleet-031-020-02-04` namespace runs two `probe` replicas behind the `probe` Service and a `shuttle` client pod. The `kube-bench` image `docker.io/aquasec/kube-bench:v0.10.6` is already loaded on both nodes. The ConfigMap `audit-request` in the `starfleet-031-020-02-04` namespace names the benchmark edition under the key `benchmark`. No kube-bench Job exists.

Open a shell on the lab VM (virtual machine) and check that kubectl uses this lab's cluster:

```sh
astrona ssh astro-ats-031-lab-020-02-04
kubectl config current-context
```

The second command prints `kubernetes-admin@astro-ats-031-lab-020-02-04`. You are logged in as the `student` user, which has a kubeconfig file for the cluster. A kubeconfig file tells `kubectl` which cluster to use and which credentials to send. Node files and processes belong to root, so run node commands with `sudo`. They change only the lab VM, not your own computer.

## Required result

- Create the Job `etcd-audit` in the `starfleet-031-020-02-04` namespace. It runs kube-bench on the control plane node with the target `etcd` only and with `--benchmark` set to the edition in `audit-request`.
- The Job completes, and its log holds the etcd checks (section `2`) and no control plane checks (section `1`).

## Verify The Result

The grader reads the command of the Job and the log of its finished pod.
