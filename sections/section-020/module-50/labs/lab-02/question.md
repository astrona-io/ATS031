---
exam_objectives:
- Use CIS benchmark to review the security configuration of Kubernetes components
  (etcd, kubelet, kubedns, kubeapi)
---
# Remediate Five Kubelet Benchmark Findings

Allow about 12 minutes for the tasks.

A benchmark review of the `starfleet` node lists five findings for the kubelet. Remediate all of them and keep the node in service.

## Starting state

The lab VM runs a one-node Kubernetes cluster built with kubeadm, the standard tool that installs a cluster on a Linux machine. The node `astro-ats-031-lab-020-05-02` is the control plane and also runs the pods. The `starfleet-031-020-05-02` namespace runs two `probe` replicas behind the `probe` Service and a `shuttle` client pod. A copy of the original kubelet configuration is in `/opt/training/backup/kubelet-config.yaml` on the node. The review lists these findings for the node `astro-ats-031-lab-020-05-02`:

1. `/var/lib/kubelet/config.yaml` has mode `644`.
2. `/etc/kubernetes/kubelet.conf` has mode `644`.
3. `rotateCertificates` is `false`.
4. `streamingConnectionIdleTimeout` has no useful value.
5. `tlsMinVersion` is not set.

Open a shell on the lab VM (virtual machine) and check that kubectl uses this lab's cluster:

```sh
astrona ssh astro-ats-031-lab-020-05-02
kubectl config current-context
```

The second command prints `kubernetes-admin@astro-ats-031-lab-020-05-02`. You are logged in as the `student` user, which has a kubeconfig file for the cluster. A kubeconfig file tells `kubectl` which cluster to use and which credentials to send. Node files and processes belong to root, so run node commands with `sudo`. They change only the lab VM, not your own computer.

## Required result

- `/var/lib/kubelet/config.yaml` and `/etc/kubernetes/kubelet.conf` on the node have mode `600` or stricter and the owner `root:root`.
- The effective kubelet configuration has `rotateCertificates` set to `true`.
- The effective `streamingConnectionIdleTimeout` is `5m0s`.
- The effective `tlsMinVersion` is `VersionTLS12` or `VersionTLS13`.
- The node is `Ready`, and both `probe` replicas stay available.

## Verify The Result

The grader reads the file modes with `stat` on the node and the effective kubelet configuration through the `configz` endpoint of the API server.
