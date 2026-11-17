---
exam_objectives:
- Use CIS benchmark to review the security configuration of Kubernetes components
  (etcd, kubelet, kubedns, kubeapi)
---
# Close The Kubelet Read-Only Port And Raise Its TLS Minimum

Allow about 10 minutes for the tasks.

From the `shuttle` pod in the `starfleet` cluster, anyone can read the pod list of the worker node over plain HTTP. The kubelet also still accepts TLS 1.0. Fix both.

## Starting state

The kind cluster has one control plane node and one worker node. The `starfleet-031-020-05-04` namespace runs two `probe` replicas behind the `probe` Service and a `shuttle` client pod. The kubelet on the worker node serves the read-only port `10255` and accepts TLS 1.0. A copy of the original kubelet configuration is in `/opt/training/backup/kubelet-config.yaml` on the worker node.

Connect to this lab from a host shell. The command `astrona kubeconfig` prints the path of the lab's kubeconfig, the file that tells `kubectl` which cluster to use and which credentials to send. The two variables hold the names of the node containers: `node_name` is the control plane node and `worker_name` is the worker node.

```sh
export KUBECONFIG="$(astrona kubeconfig ats-031-lab-020-05-04)"
test "$(kubectl config current-context)" = "kind-astro-ats-031-lab-020-05-04" || exit 1
node_name="astro-ats-031-lab-020-05-04-control-plane"
worker_name="astro-ats-031-lab-020-05-04-worker"
```

Run node commands as `podman exec "$node_name" ...` or `podman exec "$worker_name" ...`. They change only the node containers of this lab, not your own computer.

## Required result

- The effective configuration of the kubelet on the worker node `astro-ats-031-lab-020-05-04-worker` has `readOnlyPort` set to `0`.
- A request from the `shuttle` pod to `http://<worker-ip>:10255/pods` fails.
- The effective `tlsMinVersion` is `VersionTLS12` or `VersionTLS13`.
- The worker node is `Ready`, and both `probe` replicas stay available.

## Verify The Result

The grader reads the effective kubelet configuration through the `configz` endpoint and sends a request from the `shuttle` pod to the read-only port of the worker node.
