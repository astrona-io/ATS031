---
exam_objectives:
- Use CIS benchmark to review the security configuration of Kubernetes components
  (etcd, kubelet, kubedns, kubeapi)
---
# Starting Environment

The kind cluster has one control plane node and one worker node. The `starfleet-031-020-03-05` namespace runs two `probe` replicas behind the `probe` Service and a `shuttle` client pod. The API server runs without the `NodeRestriction` admission plugin.

Enable the NodeRestriction admission plugin on the API server, then use the worker kubelet credentials to prove that a kubelet can no longer set a `node-restriction.kubernetes.io/` label.
