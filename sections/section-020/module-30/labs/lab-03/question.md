---
exam_objectives:
- Use CIS benchmark to review the security configuration of Kubernetes components
  (etcd, kubelet, kubedns, kubeapi)
---
# Recover A Broken Controller Manager Static Pod

Allow about 10 minutes for the tasks.

Someone edited the controller manager manifest on the `starfleet` control plane during the night shift. Since then, new pods of Deployments are no longer created. Bring the controller manager back.

## Starting state

The lab VM runs a one-node Kubernetes cluster built with kubeadm, the standard tool that installs a cluster on a Linux machine. The node `astro-ats-031-lab-020-03-03` is the control plane and also runs the pods. The `starfleet-031-020-03-03` namespace runs two `probe` replicas behind the `probe` Service and a `shuttle` client pod. The kube-controller-manager static pod fails to start after a manual edit of its manifest. A copy of the manifest from before the edit is in `/opt/training/backup/kube-controller-manager.yaml` on the control plane node.

Open a shell on the lab VM (virtual machine) and check that kubectl uses this lab's cluster:

```sh
astrona ssh astro-ats-031-lab-020-03-03
kubectl config current-context
```

The second command prints `kubernetes-admin@astro-ats-031-lab-020-03-03`. You are logged in as the `student` user, which has a kubeconfig file for the cluster. A kubeconfig file tells `kubectl` which cluster to use and which credentials to send. Node files and processes belong to root, so run node commands with `sudo`. They change only the lab VM, not your own computer.

## Required result

- The kube-controller-manager process runs again on the control plane node, and the pod `kube-controller-manager-<node>` in `kube-system` is ready.
- The manifest `/etc/kubernetes/manifests/kube-controller-manager.yaml` has mode `600` or stricter and the owner `root:root`.
- `/etc/kubernetes/manifests` holds only the four manifests `etcd.yaml`, `kube-apiserver.yaml`, `kube-controller-manager.yaml` and `kube-scheduler.yaml`.
- The API server stays ready and both `probe` replicas stay available.

## Verify The Result

The grader reads the command line of the running `kube-controller-manager` process, the pod status, the file mode and the list of files in the manifests directory.
