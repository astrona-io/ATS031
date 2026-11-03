---
draft: true
exam_objectives:
- Use CIS benchmark to review the security configuration of Kubernetes components
  (etcd, kubelet, kubedns, kubeapi)
---
# Starting Environment

The kind cluster has two healthy probe replicas and a `shuttle` client pod. The API server runs without an audit policy and without an audit log. An audit policy file is staged on the control plane node at `/opt/training/audit-policy.yaml`, but no component references it. A copy of every original manifest is in `/opt/training/backup` on the control plane node.
