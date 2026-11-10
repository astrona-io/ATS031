---
draft: true
exam_objectives:
- Use CIS benchmark to review the security configuration of Kubernetes components
  (etcd, kubelet, kubedns, kubeapi)
---
# Disable API Server Profiling In A Private Node

Review and correct one effective control-plane setting while keeping API access available.

The task and solution use a separate pinned kind cluster. Run `astrona test` on this folder: `testing/verify-start.sh` checks that every outcome fails on the starting state, then the reference solution is applied and every outcome must pass.
