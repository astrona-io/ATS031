---
draft: true
exam_objectives:
- Use CIS benchmark to review the security configuration of Kubernetes components
  (etcd, kubelet, kubedns, kubeapi)
---
# Remediate Five Kubelet Benchmark Findings

A benchmark review of the worker node lists five findings for the kubelet. Remediate all of them and keep the node in service.

## Starting state

The isolated environment has one control plane node, one worker node, two healthy probe replicas and two client Pods. A kubeconfig identifies the cluster and credentials used by kubectl, the Kubernetes command-line tool. The environment also has the weak authentication settings from the review, but only the five findings below are graded in this task.

Use a host shell with the private kubeconfig for this independent kind environment.

```sh
export KUBECONFIG="$(astrona kubeconfig ats-031-lab-020-05-02)"
test "$(kubectl config current-context)" = "kind-astro-ats-031-lab-020-05-02" || exit 1
node_name="astro-ats-031-lab-020-05-02-control-plane"
worker_name="astro-ats-031-lab-020-05-02-worker"
```

Keep this connection selected. Host-level commands name only this environment's node containers. They do not operate on the host operating system.

## Findings

1. `/var/lib/kubelet/config.yaml` on the worker node has mode `644`. The benchmark requires `600` or stricter.
2. `/etc/kubernetes/kubelet.conf` on the worker node has mode `644`. The benchmark requires `600` or stricter.
3. `rotateCertificates` is `false`. It must be `true`.
4. `streamingConnectionIdleTimeout` is not set to a useful value. It must be `5m0s` in the effective configuration.
5. `tlsMinVersion` is not set. It must be `VersionTLS12`.

## Required result

All five findings are fixed in the effective state. The worker node is `Ready` and both application replicas stay available. Do not set `protectKernelDefaults`, because a kind node shares the kernel of the host.

## Verify The Result

The grader reads the file modes with `stat` on the worker node and the effective kubelet configuration through the API server. Restart the kubelet and wait until the effective configuration shows your change. A duplicate key in the kubelet file stops the kubelet, so remove a key before you append it again. A copy of the original file is in `/opt/training/backup` on the worker node.
