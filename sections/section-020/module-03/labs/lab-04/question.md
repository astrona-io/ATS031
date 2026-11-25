---
exam_objectives:
- Use CIS benchmark to review the security configuration of Kubernetes components
  (etcd, kubelet, kubedns, kubeapi)
---
# Restore API Server Authorization And Remove Anonymous Access

Allow about 12 minutes for the tasks.

A test on the `starfleet` cluster shows that a request without any credentials can list pods. Find both causes and close them.

## Starting state

The lab VM runs a one-node Kubernetes cluster built with kubeadm, the standard tool that installs a cluster on a Linux machine. The node `astro-ats-031-lab-020-03-04` is the control plane and also runs the pods. The `starfleet-031-020-03-04` namespace runs two `probe` replicas behind the `probe` Service and a `shuttle` client pod. The API server allows every request, and an extra RBAC binding grants read access to anonymous requests. The lab does not tell you the name of the binding.

Open a shell on the lab VM (virtual machine) and check that kubectl uses this lab's cluster:

```sh
astrona ssh astro-ats-031-lab-020-03-04
kubectl config current-context
```

The second command prints `kubernetes-admin@astro-ats-031-lab-020-03-04`. You are logged in as the `student` user, which has a kubeconfig file for the cluster. A kubeconfig file tells `kubectl` which cluster to use and which credentials to send. Node files and processes belong to root, so run node commands with `sudo`. They change only the lab VM, not your own computer.

## Required result

- The API server on the control plane node runs with `--authorization-mode=Node,RBAC` and without `AlwaysAllow`.
- An anonymous request (no client certificate and no token) to `https://127.0.0.1:6443/api/v1/namespaces/starfleet-031-020-03-04/pods` on the control plane node returns HTTP `401` or `403`.
- The health path `/readyz` still answers anonymous requests, because the kubelet probes of the API server use it. Do not set `--anonymous-auth=false`.
- Both `probe` replicas stay available.

## Verify The Result

The grader reads the command line of the running `kube-apiserver` process and sends an anonymous request with `curl` from the control plane node.
