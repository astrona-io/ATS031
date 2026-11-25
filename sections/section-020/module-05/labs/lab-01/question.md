---
exam_objectives:
- Use CIS benchmark to review the security configuration of Kubernetes components
  (etcd, kubelet, kubedns, kubeapi)
---
# Secure Kubelet Authentication And Authorization

Allow about 12 minutes for the tasks.

A scan of the `starfleet` node shows that anyone who reaches port `10250` can list the pods on the node. Close the kubelet API.

## Starting state

The lab VM runs a one-node Kubernetes cluster built with kubeadm, the standard tool that installs a cluster on a Linux machine. The node `astro-ats-031-lab-020-05-01` is the control plane and also runs the pods. The `starfleet-031-020-05-01` namespace runs two `probe` replicas behind the `probe` Service and a `shuttle` client pod. The kubelet on the node accepts anonymous requests and allows every request (`AlwaysAllow`). A copy of the original kubelet configuration is in `/opt/training/backup/kubelet-config.yaml` on the node.

Open a shell on the lab VM (virtual machine) and check that kubectl uses this lab's cluster:

```sh
astrona ssh astro-ats-031-lab-020-05-01
kubectl config current-context
```

The second command prints `kubernetes-admin@astro-ats-031-lab-020-05-01`. You are logged in as the `student` user, which has a kubeconfig file for the cluster. A kubeconfig file tells `kubectl` which cluster to use and which credentials to send. Node files and processes belong to root, so run node commands with `sudo`. They change only the lab VM, not your own computer.

## Required result

- The kubelet on the node `astro-ats-031-lab-020-05-01` runs with `authentication.anonymous.enabled: false` and `authorization.mode: Webhook` in its effective configuration.
- A request without credentials on the node to `https://<node-ip>:10250/pods` returns HTTP `401`.
- The node is `Ready`, and both `probe` replicas stay available.

## Verify The Result

The grader reads the effective kubelet configuration through the `configz` endpoint and sends an anonymous request to the kubelet API on the node.
