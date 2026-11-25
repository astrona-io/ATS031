---
exam_objectives:
- Use CIS benchmark to review the security configuration of Kubernetes components
  (etcd, kubelet, kubedns, kubeapi)
---
# Correct The Scheduler Bind Address And Record It

Allow about 10 minutes for the tasks.

A benchmark run on the `starfleet` control plane reports that the scheduler accepts connections on every address of the node. Correct the finding and record it for the review.

## Starting state

The lab VM runs a one-node Kubernetes cluster built with kubeadm, the standard tool that installs a cluster on a Linux machine. The node `astro-ats-031-lab-020-01-01` is the control plane and also runs the pods. The `starfleet-031-020-01-01` namespace runs two `probe` replicas behind the `probe` Service and a `shuttle` client pod. The kube-scheduler static pod runs with `--bind-address=0.0.0.0`, so its secure port `10259` listens on every address of the control plane node.

Open a shell on the lab VM (virtual machine) and check that kubectl uses this lab's cluster:

```sh
astrona ssh astro-ats-031-lab-020-01-01
kubectl config current-context
```

The second command prints `kubernetes-admin@astro-ats-031-lab-020-01-01`. You are logged in as the `student` user, which has a kubeconfig file for the cluster. A kubeconfig file tells `kubectl` which cluster to use and which credentials to send. Node files and processes belong to root, so run node commands with `sudo`. They change only the lab VM, not your own computer.

## Required result

- The kube-scheduler on the control plane node runs with `--bind-address=127.0.0.1`, so its port `10259` answers only on `127.0.0.1`.
- Keep any backup of the manifest outside `/etc/kubernetes/manifests`.
- Create the ConfigMap `benchmark-review` in the `starfleet-031-020-01-01` namespace with `component: kube-scheduler`, `check: 1.4.2`, `setting: bind-address` and `result: corrected`.
- The kube-scheduler pod is running again, the API server stays ready and both `probe` replicas stay available.

## Verify The Result

The grader reads the command line of the running `kube-scheduler` process, not only the manifest, and connects to port `10259` on the loopback address and on the node address. It also reads the ConfigMap.
