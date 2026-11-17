---
exam_objectives:
- Use CIS benchmark to review the security configuration of Kubernetes components
  (etcd, kubelet, kubedns, kubeapi)
---
# Starting Environment

The kind cluster has one control plane node and one worker node. The `starfleet-031-020-03-04` namespace runs two `probe` replicas behind the `probe` Service and a `shuttle` client pod. The API server allows every request, and an extra RBAC binding grants read access to anonymous requests. The lab does not tell you the name of the binding.

Restore the `Node,RBAC` authorization mode of the API server and remove the RBAC binding that lets anonymous requests read the cluster.
