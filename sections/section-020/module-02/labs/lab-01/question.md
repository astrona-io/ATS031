---
exam_objectives:
- Use CIS benchmark to review the security configuration of Kubernetes components
  (etcd, kubelet, kubedns, kubeapi)
---
# Save The Failing API Server Check Ids

Allow about 12 minutes for the tasks.

The security team of the `starfleet` cluster needs the list of failing API server checks in a form that a script can read, before it plans fixes.

## Starting state

The lab VM runs a one-node Kubernetes cluster built with kubeadm, the standard tool that installs a cluster on a Linux machine. The node `astro-ats-031-lab-020-02-01` is the control plane and also runs the pods. The `starfleet-031-020-02-01` namespace runs two `probe` replicas behind the `probe` Service and a `shuttle` client pod. The `kube-bench` image `docker.io/aquasec/kube-bench:v0.10.6` is already loaded on both nodes. The control plane node runs with the kubeadm defaults. No kube-bench result has been collected.

Open a shell on the lab VM (virtual machine) and check that kubectl uses this lab's cluster:

```sh
astrona ssh astro-ats-031-lab-020-02-01
kubectl config current-context
```

The second command prints `kubernetes-admin@astro-ats-031-lab-020-02-01`. You are logged in as the `student` user, which has a kubeconfig file for the cluster. A kubeconfig file tells `kubectl` which cluster to use and which credentials to send. Node files and processes belong to root, so run node commands with `sudo`. They change only the lab VM, not your own computer.

## Required result

- Create the Job `api-server-audit` in the `starfleet-031-020-02-01` namespace. It runs `kube-bench run --targets master --json` on the control plane node and completes.
- From its JSON output, find every check with the status `FAIL` whose number starts with `1.2.`.
- Create the ConfigMap `failing-checks` in the same namespace with the numbers under the key `ids`, one number on each line.

Do not change any setting of the cluster. The grader runs kube-bench again and compares its failing `1.2.` checks with your list.

## Verify The Result

The grader reads your Job, then runs its own JSON audit in the same namespace and compares the result with your ConfigMap. A list that is too short, too long, or that holds a number outside `1.2.` fails.
