---
exam_objectives:
- Use CIS benchmark to review the security configuration of Kubernetes components
  (etcd, kubelet, kubedns, kubeapi)
---
# Starting Environment

The kind cluster has one control plane node and one worker node. The `starfleet-031-020-05-06` namespace runs two `probe` replicas behind the `probe` Service and a `shuttle` client pod. The `outpost-031-020-05-06` namespace runs the `drifter` pod with its default service account. An RBAC grant in `kube-system` lets that service account change ConfigMaps there. The lab does not tell you the names of the objects.

Find the RBAC grant that lets a workload service account change the CoreDNS ConfigMap, remove it, and switch the Corefile to verified pod records without breaking name resolution.
