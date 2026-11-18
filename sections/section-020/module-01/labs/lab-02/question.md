---
exam_objectives:
- Use CIS benchmark to review the security configuration of Kubernetes components
  (etcd, kubelet, kubedns, kubeapi)
---
# Restrict Control Plane Kubeconfig And Key Files

Allow about 8 minutes for the tasks.

A file scan of the `starfleet` control plane node reports that some credential files can be read by every local user. Find them and close them.

## Starting state

The lab VM runs a one-node Kubernetes cluster built with kubeadm, the standard tool that installs a cluster on a Linux machine. The node `astro-ats-031-lab-020-01-02` is the control plane and also runs the pods. The `starfleet-031-020-01-02` namespace runs two `probe` replicas behind the `probe` Service and a `shuttle` client pod. Some files in `/etc/kubernetes` and `/etc/kubernetes/pki` on the control plane node have mode `644`. The lab does not tell you which ones.

Open a shell on the lab VM (virtual machine) and check that kubectl uses this lab's cluster:

```sh
astrona ssh astro-ats-031-lab-020-01-02
kubectl config current-context
```

The second command prints `kubernetes-admin@astro-ats-031-lab-020-01-02`. You are logged in as the `student` user, which has a kubeconfig file for the cluster. A kubeconfig file tells `kubectl` which cluster to use and which credentials to send. Node files and processes belong to root, so run node commands with `sudo`. They change only the lab VM, not your own computer.

## Required result

- Every kubeconfig file `/etc/kubernetes/*.conf` on the control plane node has mode `600` or stricter and the owner `root:root`.
- Every private key file (`*.key`) under `/etc/kubernetes/pki` on the control plane node has mode `600` or stricter and the owner `root:root`.
- The API server stays ready and both `probe` replicas stay available.

Do not change certificate files (`*.crt`); the benchmark allows mode `644` for them.

## Verify The Result

The grader runs `stat` on every matching file on the control plane node. A mode such as `400` also passes, because it is stricter than `600`.
