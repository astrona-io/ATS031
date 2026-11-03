---
draft: true
exam_objectives:
- Use CIS benchmark to review the security configuration of Kubernetes components
  (etcd, kubelet, kubedns, kubeapi)
---
# Starting Environment

The kind cluster has two healthy probe replicas and a `shuttle` client pod. The API server runs with profiling at its default value, and the permissions of its static pod manifest are wider than the benchmark allows. A copy of every original manifest is in `/opt/training/backup` on the control plane node.
