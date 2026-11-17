---
exam_objectives:
- Use CIS benchmark to review the security configuration of Kubernetes components
  (etcd, kubelet, kubedns, kubeapi)
---
# Enable NodeRestriction

Enable the NodeRestriction admission plugin on the API server, then use the worker kubelet credentials to prove that a kubelet can no longer set a `node-restriction.kubernetes.io/` label.

The task and solution use a separate pinned kind cluster with one control plane node and one worker node. Run `astrona test` on this folder: `testing/verify-start.sh` checks that every outcome fails on the starting state, then `solution/apply.sh` applies the reference solution and every outcome must pass.
