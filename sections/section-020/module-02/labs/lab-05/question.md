---
exam_objectives:
- Use CIS benchmark to review the security configuration of Kubernetes components
  (etcd, kubelet, kubedns, kubeapi)
---
# Record The Totals Of A kube-bench Report

Allow about 10 minutes for the tasks.

The `starfleet` platform team tracks its benchmark progress in numbers. Run the control plane audit and record the numbers of this run.

## Starting state

The lab VM runs a one-node Kubernetes cluster built with kubeadm, the standard tool that installs a cluster on a Linux machine. The node `astro-ats-031-lab-020-02-05` is the control plane and also runs the pods. The `starfleet-031-020-02-05` namespace runs two `probe` replicas behind the `probe` Service and a `shuttle` client pod. The `kube-bench` image `docker.io/aquasec/kube-bench:v0.10.6` is already loaded on both nodes. No kube-bench Job exists.

Open a shell on the lab VM (virtual machine) and check that kubectl uses this lab's cluster:

```sh
astrona ssh astro-ats-031-lab-020-02-05
kubectl config current-context
```

The second command prints `kubernetes-admin@astro-ats-031-lab-020-02-05`. You are logged in as the `student` user, which has a kubeconfig file for the cluster. A kubeconfig file tells `kubectl` which cluster to use and which credentials to send. Node files and processes belong to root, so run node commands with `sudo`. They change only the lab VM, not your own computer.

## Required result

- Create the Job `master-audit` in the `starfleet-031-020-02-05` namespace. It runs `kube-bench run --targets master` on the control plane node and completes.
- Create the ConfigMap `master-result` in the same namespace with these keys, all read from the log of `master-audit`:
  - `pass`, `fail`, `warn` and `info`: the totals in the summary at the end of the log.
  - `fail-1.1`: the number of `[FAIL]` lines for checks in section `1.1` (control plane node configuration files).
  - `fail-1.2`: the number of `[FAIL]` lines for checks in section `1.2` (API server).

## Verify The Result

The grader reads the log of your finished `master-audit` pod and compares its summary and its `[FAIL]` lines with your ConfigMap. Do not change the cluster after the run.
