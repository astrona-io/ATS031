---
exam_objectives:
- Use CIS benchmark to review the security configuration of Kubernetes components
  (etcd, kubelet, kubedns, kubeapi)
---
# Restore API Server Authorization And Remove Anonymous Access

Allow about 12 minutes for the tasks.

A test on the `starfleet` cluster shows that a request without any credentials can list pods. Find both causes and close them.

## Starting state

The kind cluster has one control plane node and one worker node. The `starfleet-031-020-03-04` namespace runs two `probe` replicas behind the `probe` Service and a `shuttle` client pod. The API server allows every request, and an extra RBAC binding grants read access to anonymous requests. The lab does not tell you the name of the binding.

Connect to this lab from a host shell. The command `astrona kubeconfig` prints the path of the lab's kubeconfig, the file that tells `kubectl` which cluster to use and which credentials to send. The two variables hold the names of the node containers: `node_name` is the control plane node and `worker_name` is the worker node.

```sh
export KUBECONFIG="$(astrona kubeconfig ats-031-lab-020-03-04)"
test "$(kubectl config current-context)" = "kind-astro-ats-031-lab-020-03-04" || exit 1
node_name="astro-ats-031-lab-020-03-04-control-plane"
worker_name="astro-ats-031-lab-020-03-04-worker"
```

Run node commands as `podman exec "$node_name" ...` or `podman exec "$worker_name" ...`. They change only the node containers of this lab, not your own computer.

## Required result

- The API server on the control plane node runs with `--authorization-mode=Node,RBAC` and without `AlwaysAllow`.
- An anonymous request (no client certificate and no token) to `https://127.0.0.1:6443/api/v1/namespaces/starfleet-031-020-03-04/pods` on the control plane node returns HTTP `401` or `403`.
- The health path `/readyz` still answers anonymous requests, because the kubelet probes of the API server use it. Do not set `--anonymous-auth=false`.
- Both `probe` replicas stay available.

## Verify The Result

The grader reads the command line of the running `kube-apiserver` process and sends an anonymous request with `curl` from the control plane node.
