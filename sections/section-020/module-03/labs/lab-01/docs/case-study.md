---
exam_objectives:
- Use CIS benchmark to review the security configuration of Kubernetes components
  (etcd, kubelet, kubedns, kubeapi)
---
# Starting Environment

The kind cluster has one control plane node and one worker node. The `starfleet-031-020-03-01` namespace runs two `probe` replicas behind the `probe` Service and a `shuttle` client pod. An audit policy is staged in `/opt/training/audit-policy.yaml` on the control plane node. No component uses it yet, and the API server writes no audit log.

Enable audit logging on the API server with a staged policy, set the log retention, and prove that the API server writes an event.
