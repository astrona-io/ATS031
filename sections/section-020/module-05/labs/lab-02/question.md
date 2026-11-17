---
exam_objectives:
- Use CIS benchmark to review the security configuration of Kubernetes components
  (etcd, kubelet, kubedns, kubeapi)
---
# Remediate Five Kubelet Benchmark Findings

Allow about 12 minutes for the tasks.

A benchmark review of the `starfleet` worker node lists five findings for the kubelet. Remediate all of them and keep the node in service.

## Starting state

The kind cluster has one control plane node and one worker node. The `starfleet-031-020-05-02` namespace runs two `probe` replicas behind the `probe` Service and a `shuttle` client pod. A copy of the original kubelet configuration is in `/opt/training/backup/kubelet-config.yaml` on the worker node. The review lists these findings for the worker node `astro-ats-031-lab-020-05-02-worker`:

1. `/var/lib/kubelet/config.yaml` has mode `644`.
2. `/etc/kubernetes/kubelet.conf` has mode `644`.
3. `rotateCertificates` is `false`.
4. `streamingConnectionIdleTimeout` has no useful value.
5. `tlsMinVersion` is not set.

Connect to this lab from a host shell. The command `astrona kubeconfig` prints the path of the lab's kubeconfig, the file that tells `kubectl` which cluster to use and which credentials to send. The two variables hold the names of the node containers: `node_name` is the control plane node and `worker_name` is the worker node.

```sh
export KUBECONFIG="$(astrona kubeconfig ats-031-lab-020-05-02)"
test "$(kubectl config current-context)" = "kind-astro-ats-031-lab-020-05-02" || exit 1
node_name="astro-ats-031-lab-020-05-02-control-plane"
worker_name="astro-ats-031-lab-020-05-02-worker"
```

Run node commands as `podman exec "$node_name" ...` or `podman exec "$worker_name" ...`. They change only the node containers of this lab, not your own computer.

## Required result

- `/var/lib/kubelet/config.yaml` and `/etc/kubernetes/kubelet.conf` on the worker node have mode `600` or stricter and the owner `root:root`.
- The effective kubelet configuration has `rotateCertificates` set to `true`.
- The effective `streamingConnectionIdleTimeout` is `5m0s`.
- The effective `tlsMinVersion` is `VersionTLS12` or `VersionTLS13`.
- The worker node is `Ready`, and both `probe` replicas stay available. Do not set `protectKernelDefaults`, because a kind node shares the kernel of the host.

## Verify The Result

The grader reads the file modes with `stat` on the worker node and the effective kubelet configuration through the `configz` endpoint of the API server.
