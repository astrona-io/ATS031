---
exam_objectives:
- Use CIS benchmark to review the security configuration of Kubernetes components
  (etcd, kubelet, kubedns, kubeapi)
---
# Run The Node Checks With A kube-bench Job

Allow about 10 minutes for the tasks.

The `starfleet` cluster has a control plane report, but nobody has run the worker node checks of the benchmark on its node yet. Run that audit.

## Starting state

The lab VM runs a one-node Kubernetes cluster built with kubeadm, the standard tool that installs a cluster on a Linux machine. The node `astro-ats-031-lab-020-02-03` is the control plane and also runs the pods. The `starfleet-031-020-02-03` namespace runs two `probe` replicas behind the `probe` Service and a `shuttle` client pod. The `kube-bench` image `docker.io/aquasec/kube-bench:v0.10.6` is already loaded on the node. No kube-bench Job exists.

Open a shell on the lab VM (virtual machine) and check that kubectl uses this lab's cluster:

```sh
astrona ssh astro-ats-031-lab-020-02-03
kubectl config current-context
```

The second command prints `kubernetes-admin@astro-ats-031-lab-020-02-03`. You are logged in as the `student` user, which has a kubeconfig file for the cluster. A kubeconfig file tells `kubectl` which cluster to use and which credentials to send. Node files and processes belong to root, so run node commands with `sudo`. They change only the lab VM, not your own computer.

## Required result

- Create the Job `node-audit` in the `starfleet-031-020-02-03` namespace. It runs `kube-bench run --targets node` with the image `docker.io/aquasec/kube-bench:v0.10.6`.
- The pod runs on the node `astro-ats-031-lab-020-02-03`, shares the process namespace of the node (`hostPID: true`) and mounts the node directories that the audit reads.
- The Job completes, and its log holds the results of the worker node section of the benchmark.

## Verify The Result

The grader reads the Job, the node of its pod and the log of the pod. A log without worker node results fails, for example when the pod could not read the kubelet process.
