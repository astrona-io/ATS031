---
exam_objectives:
- Use CIS benchmark to review the security configuration of Kubernetes components
  (etcd, kubelet, kubedns, kubeapi)
---
# Remove A Kubelet Flag That Overrides The Configuration File

Allow about 10 minutes for the tasks.

The kubelet configuration file on the `starfleet` node says `Webhook`, but a scan reports that the kubelet allows every request. Find the source of the real value and fix it.

## Starting state

The lab VM runs a one-node Kubernetes cluster built with kubeadm, the standard tool that installs a cluster on a Linux machine. The node `astro-ats-031-lab-020-05-03` is the control plane and also runs the pods. The `starfleet-031-020-05-03` namespace runs two `probe` replicas behind the `probe` Service and a `shuttle` client pod. The file `/var/lib/kubelet/config.yaml` on the node sets `authorization.mode: Webhook`. A copy of the kubelet files is in `/opt/training/backup` on the node.

Open a shell on the lab VM (virtual machine) and check that kubectl uses this lab's cluster:

```sh
astrona ssh astro-ats-031-lab-020-05-03
kubectl config current-context
```

The second command prints `kubernetes-admin@astro-ats-031-lab-020-05-03`. You are logged in as the `student` user, which has a kubeconfig file for the cluster. A kubeconfig file tells `kubectl` which cluster to use and which credentials to send. Node files and processes belong to root, so run node commands with `sudo`. They change only the lab VM, not your own computer.

## Required result

- The effective configuration of the kubelet on the node `astro-ats-031-lab-020-05-03` has `authorization.mode` set to `Webhook`.
- No kubelet source sets the authorization mode on the command line: neither `/var/lib/kubelet/kubeadm-flags.env` nor the running kubelet process has an `--authorization-mode` flag.
- The node is `Ready`, and both `probe` replicas stay available.

## Verify The Result

The grader reads the flags file and the command line of the running `kubelet` process on the node, and the effective configuration through the `configz` endpoint of the API server.
