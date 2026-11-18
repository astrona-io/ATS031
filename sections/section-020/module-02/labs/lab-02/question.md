---
exam_objectives:
- Use CIS benchmark to review the security configuration of Kubernetes components
  (etcd, kubelet, kubedns, kubeapi)
---
# Read A kube-bench Check Definition

Allow about 8 minutes for the tasks.

A reviewer of the `starfleet` cluster wants to know what kube-bench really tests for API server profiling in one benchmark edition. Read it from the definition files, not from a report.

## Starting state

The lab VM runs a one-node Kubernetes cluster built with kubeadm, the standard tool that installs a cluster on a Linux machine. The node `astro-ats-031-lab-020-02-02` is the control plane and also runs the pods. The `starfleet-031-020-02-02` namespace runs two `probe` replicas behind the `probe` Service and a `shuttle` client pod. The `kube-bench` image `docker.io/aquasec/kube-bench:v0.10.6` is already loaded on both nodes. The ConfigMap `audit-request` in the `starfleet-031-020-02-02` namespace names one benchmark edition under the key `edition`.

Open a shell on the lab VM (virtual machine) and check that kubectl uses this lab's cluster:

```sh
astrona ssh astro-ats-031-lab-020-02-02
kubectl config current-context
```

The second command prints `kubernetes-admin@astro-ats-031-lab-020-02-02`. You are logged in as the `student` user, which has a kubeconfig file for the cluster. A kubeconfig file tells `kubectl` which cluster to use and which credentials to send. Node files and processes belong to root, so run node commands with `sudo`. They change only the lab VM, not your own computer.

## Required result

Create the ConfigMap `check-definition` in the `starfleet-031-020-02-02` namespace with two keys:

- `files`: the names of the files in the directory of the requested edition inside the image (`/opt/kube-bench/cfg/<edition>`), one name on each line.
- `apiserver-profiling-check`: the `id` of the check in the `master.yaml` file of that edition whose `text` asks for the API server `--profiling` argument. Its `id` starts with `1.2.`.

Do not run an audit and do not change the cluster.

## Verify The Result

The grader starts its own short pod with the same image, lists the directory of the requested edition and reads its `master.yaml` file. The order of the file names does not matter.
