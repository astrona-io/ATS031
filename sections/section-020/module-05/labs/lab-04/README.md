---
exam_objectives:
- Use CIS benchmark to review the security configuration of Kubernetes components
  (etcd, kubelet, kubedns, kubeapi)
---
# Close The Kubelet Read-Only Port And Raise Its TLS Minimum

Close the plain HTTP read-only port of the kubelet and raise the lowest TLS version it accepts, then prove both from a pod and from the effective configuration.

The task and solution use a separate pinned kind cluster with one control plane node and one worker node. Run `astrona test` on this folder: `testing/verify-start.sh` checks that every outcome fails on the starting state, then `solution/apply.sh` applies the reference solution and every outcome must pass.
