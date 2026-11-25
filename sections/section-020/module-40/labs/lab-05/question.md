---
exam_objectives:
- Use CIS benchmark to review the security configuration of Kubernetes components
  (etcd, kubelet, kubedns, kubeapi)
---
# Find A Secret Directly In etcd

Allow about 10 minutes for the tasks.

A Secret called `relay-token` exists somewhere in the `starfleet` cluster. The security team wants to see where etcd stores it, without asking the API server.

## Starting state

The lab VM runs a one-node Kubernetes cluster built with kubeadm, the standard tool that installs a cluster on a Linux machine. The node `astro-ats-031-lab-020-04-05` is the control plane and also runs the pods. The `starfleet-031-020-04-05` namespace runs two `probe` replicas behind the `probe` Service and a `shuttle` client pod. etcd runs as a static pod on the control plane node. A Secret called `relay-token` exists in one namespace of the cluster. The lab does not tell you which namespace.

Open a shell on the lab VM (virtual machine) and check that kubectl uses this lab's cluster:

```sh
astrona ssh astro-ats-031-lab-020-04-05
kubectl config current-context
```

The second command prints `kubernetes-admin@astro-ats-031-lab-020-04-05`. You are logged in as the `student` user, which has a kubeconfig file for the cluster. A kubeconfig file tells `kubectl` which cluster to use and which credentials to send. Node files and processes belong to root, so run node commands with `sudo`. They change only the lab VM, not your own computer.

## Required result

Use `etcdctl` against etcd, not `kubectl get secret`, to find the Secret. Then create the ConfigMap `etcd-query` in the `starfleet-031-020-04-05` namespace with these keys:

- `secret-key`: the full etcd key of the Secret `relay-token`, for example `/registry/secrets/<namespace>/relay-token`.
- `secret-namespace`: the namespace that the key names.
- `member-name`: the name of the etcd member, as `etcdctl member list` prints it.

## Verify The Result

The grader asks the API server where `relay-token` is and reads the `--name` flag of the running `etcd` process.
