---
exam_objectives:
- Use CIS benchmark to review the security configuration of Kubernetes components
  (etcd, kubelet, kubedns, kubeapi)
---
# Require Client Certificates On etcd

Allow about 12 minutes for the tasks.

A scan of the `starfleet` control plane reports that etcd answers requests that bring no certificate. Close the gap.

## Starting state

The lab VM runs a one-node Kubernetes cluster built with kubeadm, the standard tool that installs a cluster on a Linux machine. The node `astro-ats-031-lab-020-04-03` is the control plane and also runs the pods. The `starfleet-031-020-04-03` namespace runs two `probe` replicas behind the `probe` Service and a `shuttle` client pod. etcd runs as a static pod on the control plane node. Someone turned off client certificate authentication for the client and the peer ports of etcd. A copy of the etcd manifest from before that change is in `/opt/training/backup/etcd.yaml` on the control plane node.

Open a shell on the lab VM (virtual machine) and check that kubectl uses this lab's cluster:

```sh
astrona ssh astro-ats-031-lab-020-04-03
kubectl config current-context
```

The second command prints `kubernetes-admin@astro-ats-031-lab-020-04-03`. You are logged in as the `student` user, which has a kubeconfig file for the cluster. A kubeconfig file tells `kubectl` which cluster to use and which credentials to send. Node files and processes belong to root, so run node commands with `sudo`. They change only the lab VM, not your own computer.

## Required result

- etcd runs with `--client-cert-auth=true` and `--peer-client-cert-auth=true`.
- A request to `https://127.0.0.1:2379/health` on the control plane node without a client certificate fails.
- The API server stays ready, and both `probe` replicas stay available.

Keep every backup outside `/etc/kubernetes/manifests`.

## Verify The Result

The grader reads the command line of the running `etcd` process and sends a request without a client certificate to the client port of etcd from the control plane node.
