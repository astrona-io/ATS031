---
exam_objectives:
- Use CIS benchmark to review the security configuration of Kubernetes components
  (etcd, kubelet, kubedns, kubeapi)
---
# Guided Practice: Harden The API Server In A Private Playground

This ungraded playground is one virtual machine (VM) that runs a single-node Kubernetes cluster built with kubeadm, the standard tool that installs a cluster on a Linux machine. The node `astro-ats-031-playground-020-03` is the control plane and also runs your pods. The API server runs with weak settings on purpose.

Because the node is a real machine, you read and change the real static pod manifests in `/etc/kubernetes/manifests`. A static pod is a pod that the kubelet starts from a manifest file on the node, without the API server. That is the same work you do on a node in the exam.

<!-- astrona:playground:renew -->

Open a shell on the node. You log in as the `student` user, which has `sudo` and a kubeconfig file for the cluster. A kubeconfig file tells kubectl, the Kubernetes command-line tool, which cluster to use and which credentials to send.

```sh
astrona ssh astro-ats-031-playground-020-03
kubectl config current-context
```

The second command prints `kubernetes-admin@astro-ats-031-playground-020-03`. Commands that use `sudo` change only this VM. They do not touch your own computer.

## Starting state

The `starfleet` namespace has the `probe` Deployment with two pods, the `probe` Service and the `shuttle` client pod. The `outpost` namespace has the `drifter` client pod. On the node, `/opt/training/audit-policy.yaml` holds an audit policy that nothing uses, and `/opt/training/backup` holds a copy of every original manifest with mode `600`. Three manifests have mode `644`.

```sh
kubectl -n starfleet get pods
sudo ls -l /etc/kubernetes/manifests /opt/training/backup
```

The two `probe` pods and the `shuttle` pod are `Running`. The first listing shows `etcd.yaml` with `-rw-------` and `kube-apiserver.yaml`, `kube-controller-manager.yaml` and `kube-scheduler.yaml` with `-rw-r--r--`. The manifests directory also holds a hidden empty file, `.kubelet-keep`, that only `ls -a` shows. The kubelet ignores files whose name starts with a dot.

## Suggested exercises

These exercises use only the node and the commands above.

1. Break the scheduler manifest with an unknown flag, read the reason with `sudo crictl logs`, and restore the backup. On this node the last log line is `Error: unknown flag: --no-such-flag`.
2. Read the authentication and authorization flags of the API server, and send an anonymous request with `curl -sk https://127.0.0.1:6443/api/v1/namespaces/kube-system/pods`. The API server answers with `403` and the user `system:anonymous`.
3. Enable audit logging with the staged policy, the log flags and the two host path mounts. On this node the API server came back after 42 seconds, and the log is `/var/log/kubernetes/audit/audit.log`.
4. Add `--profiling=false` to the API server, the controller manager and the scheduler. On this node the API server restart took 46 seconds, and `kubectl get --raw /debug/pprof/` then returns `NotFound`.
5. Set mode `600` and owner `root:root` on the widened manifests.

Always edit a copy outside `/etc/kubernetes/manifests`, move it in, and read the running pod arguments afterwards. After an API server change, wait until the mirror pod shows the new flag and `kubectl get --raw=/readyz` answers `ok`, because the pod object can show the new flag a few seconds before the new API server is ready.

## Common pitfalls

> [!WARNING]
> Keep backups outside the manifests directory. Run every command that reads `/etc/kubernetes`, `/var/log/kubernetes` or `crictl` with `sudo`; without root it fails with a permission error. A restart of the API server takes 40 to 70 seconds on this node, and `kubectl` does not answer during that time. If the API server does not come back, read the container log with `sudo crictl ps -a --name kube-apiserver` and `sudo crictl logs`, and copy the backup from `/opt/training/backup` back into place.
