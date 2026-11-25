---
exam_objectives:
- Use CIS benchmark to review the security configuration of Kubernetes components
  (etcd, kubelet, kubedns, kubeapi)
---
# Record How The API Server Connects To etcd

Allow about 8 minutes for the tasks.

Before a review of the `starfleet` control plane, the security team wants to know exactly how the API server reaches etcd and which files prove its identity.

## Starting state

The lab VM runs a one-node Kubernetes cluster built with kubeadm, the standard tool that installs a cluster on a Linux machine. The node `astro-ats-031-lab-020-04-02` is the control plane and also runs the pods. The `starfleet-031-020-04-02` namespace runs two `probe` replicas behind the `probe` Service and a `shuttle` client pod. etcd runs as a static pod on the control plane node.

Open a shell on the lab VM (virtual machine) and check that kubectl uses this lab's cluster:

```sh
astrona ssh astro-ats-031-lab-020-04-02
kubectl config current-context
```

The second command prints `kubernetes-admin@astro-ats-031-lab-020-04-02`. You are logged in as the `student` user, which has a kubeconfig file for the cluster. A kubeconfig file tells `kubectl` which cluster to use and which credentials to send. Node files and processes belong to root, so run node commands with `sudo`. They change only the lab VM, not your own computer.

## Required result

Create the ConfigMap `etcd-connection` in the `starfleet-031-020-04-02` namespace with these keys. Read each value from the running API server, not from memory:

- `servers`: the value of `--etcd-servers`.
- `client-certificate`: the path in `--etcd-certfile`.
- `client-key`: the path in `--etcd-keyfile`.
- `ca-file`: the path in `--etcd-cafile`.

Do not change the cluster.

## Verify The Result

The grader reads the command line of the running `kube-apiserver` process on the control plane node and compares each flag with your ConfigMap.
