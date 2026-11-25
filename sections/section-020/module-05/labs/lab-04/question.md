---
exam_objectives:
- Use CIS benchmark to review the security configuration of Kubernetes components
  (etcd, kubelet, kubedns, kubeapi)
---
# Close The Kubelet Read-Only Port And Raise Its TLS Minimum

Allow about 10 minutes for the tasks.

From the `shuttle` pod in the `starfleet` cluster, anyone can read the pod list of the node over plain HTTP. The kubelet also still accepts TLS 1.0. Fix both.

## Starting state

The lab VM runs a one-node Kubernetes cluster built with kubeadm, the standard tool that installs a cluster on a Linux machine. The node `astro-ats-031-lab-020-05-04` is the control plane and also runs the pods. The `starfleet-031-020-05-04` namespace runs two `probe` replicas behind the `probe` Service and a `shuttle` client pod. The kubelet on the node serves the read-only port `10255` and accepts TLS 1.0. A copy of the original kubelet configuration is in `/opt/training/backup/kubelet-config.yaml` on the node.

Open a shell on the lab VM (virtual machine) and check that kubectl uses this lab's cluster:

```sh
astrona ssh astro-ats-031-lab-020-05-04
kubectl config current-context
```

The second command prints `kubernetes-admin@astro-ats-031-lab-020-05-04`. You are logged in as the `student` user, which has a kubeconfig file for the cluster. A kubeconfig file tells `kubectl` which cluster to use and which credentials to send. Node files and processes belong to root, so run node commands with `sudo`. They change only the lab VM, not your own computer.

## Required result

- The effective configuration of the kubelet on the node `astro-ats-031-lab-020-05-04` has `readOnlyPort` set to `0`.
- A request from the `shuttle` pod to `http://<node-ip>:10255/pods` fails.
- The effective `tlsMinVersion` is `VersionTLS12` or `VersionTLS13`.
- The node is `Ready`, and both `probe` replicas stay available.

## Verify The Result

The grader reads the effective kubelet configuration through the `configz` endpoint and sends a request from the `shuttle` pod to the read-only port of the node.
