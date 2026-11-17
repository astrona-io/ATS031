---
exam_objectives:
- Use CIS benchmark to review the security configuration of Kubernetes components
  (etcd, kubelet, kubedns, kubeapi)
---
# Remove Write Access To The CoreDNS Configuration

Allow about 10 minutes for the tasks.

A review of the `starfleet` cluster DNS shows that a workload outside the platform team can change the CoreDNS configuration. Close that path and tighten the pod records.

## Starting state

The kind cluster has one control plane node and one worker node. The `starfleet-031-020-05-06` namespace runs two `probe` replicas behind the `probe` Service and a `shuttle` client pod. The `outpost-031-020-05-06` namespace runs the `drifter` pod with its default service account. An RBAC grant in `kube-system` lets that service account change ConfigMaps there. The lab does not tell you the names of the objects.

Connect to this lab from a host shell. The command `astrona kubeconfig` prints the path of the lab's kubeconfig, the file that tells `kubectl` which cluster to use and which credentials to send. The two variables hold the names of the node containers: `node_name` is the control plane node and `worker_name` is the worker node.

```sh
export KUBECONFIG="$(astrona kubeconfig ats-031-lab-020-05-06)"
test "$(kubectl config current-context)" = "kind-astro-ats-031-lab-020-05-06" || exit 1
node_name="astro-ats-031-lab-020-05-06-control-plane"
worker_name="astro-ats-031-lab-020-05-06-worker"
```

Run node commands as `podman exec "$node_name" ...` or `podman exec "$worker_name" ...`. They change only the node containers of this lab, not your own computer.

## Required result

- `kubectl auth can-i update configmap/coredns -n kube-system --as=system:serviceaccount:outpost-031-020-05-06:default` answers `no`, and the same is true for `patch`. Remove only the grant that causes it; do not change the `coredns` service account or its ClusterRole.
- The Corefile in the ConfigMap `coredns` in `kube-system` uses `pods verified` (or `pods disabled`) instead of `pods insecure`.
- The `shuttle` pod still resolves `probe.starfleet-031-020-05-06.svc.cluster.local`, and both `probe` replicas stay available.

## Verify The Result

The grader asks the API server with `kubectl auth can-i` for the service account, reads the Corefile and resolves the `probe` Service from the `shuttle` pod.
