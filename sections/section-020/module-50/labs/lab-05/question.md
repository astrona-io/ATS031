---
exam_objectives:
- Use CIS benchmark to review the security configuration of Kubernetes components
  (etcd, kubelet, kubedns, kubeapi)
---
# Restrict The Kubelet Service Files And Turn On Certificate Rotation

Allow about 10 minutes for the tasks.

The node review of the `starfleet` cluster lists two findings: readable kubelet service files and a kubelet that no longer renews its client certificate. Fix both.

## Starting state

The lab VM runs a one-node Kubernetes cluster built with kubeadm, the standard tool that installs a cluster on a Linux machine. The node `astro-ats-031-lab-020-05-05` is the control plane and also runs the pods. The `starfleet-031-020-05-05` namespace runs two `probe` replicas behind the `probe` Service and a `shuttle` client pod. The systemd unit files of the kubelet on the node have mode `644`, and certificate rotation is turned off. A copy of the original kubelet configuration is in `/opt/training/backup/kubelet-config.yaml` on the node.

Open a shell on the lab VM (virtual machine) and check that kubectl uses this lab's cluster:

```sh
astrona ssh astro-ats-031-lab-020-05-05
kubectl config current-context
```

The second command prints `kubernetes-admin@astro-ats-031-lab-020-05-05`. You are logged in as the `student` user, which has a kubeconfig file for the cluster. A kubeconfig file tells `kubectl` which cluster to use and which credentials to send. Node files and processes belong to root, so run node commands with `sudo`. They change only the lab VM, not your own computer.

## Required result

- The kubelet unit file and every drop-in file of the `kubelet` service on the node `astro-ats-031-lab-020-05-05` have mode `600` or stricter and the owner `root:root`. Find the files with `systemctl`.
- The effective configuration of the kubelet has `rotateCertificates` set to `true`.
- The node is `Ready`, and both `probe` replicas stay available.

## Verify The Result

The grader asks systemd on the node for the unit file and the drop-in files of the `kubelet` service, reads their modes with `stat`, and reads the effective kubelet configuration through the `configz` endpoint.
