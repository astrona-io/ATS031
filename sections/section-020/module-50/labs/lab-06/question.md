# Remove Write Access To The CoreDNS Configuration

A review of the cluster DNS shows that the default service account of namespace `outpost-031-020-05-06` can change the CoreDNS configuration through an RBAC grant in `kube-system`. The lab does not tell you the names of the objects. Close that path and tighten the pod records.

1. `kubectl auth can-i update configmap/coredns -n kube-system --as=system:serviceaccount:outpost-031-020-05-06:default` answers `no`, and the same is true for `patch`.
2. Remove only the grant that causes it: the `coredns` service account keeps its `system:coredns` ClusterRoleBinding and can still watch endpoints, services, pods, namespaces and endpointslices.
3. The Corefile in the ConfigMap `coredns` in `kube-system` uses `pods verified` (or `pods disabled`) instead of `pods insecure`, and the `shuttle` pod in `starfleet-031-020-05-06` still resolves `probe.starfleet-031-020-05-06.svc.cluster.local`.

Every step uses `kubectl` only; no step runs a command on a node.

Do not change the `system:coredns` ClusterRole. Both `probe` replicas must stay available.
