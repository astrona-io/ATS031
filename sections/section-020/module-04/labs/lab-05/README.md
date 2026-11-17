---
exam_objectives:
- Use CIS benchmark to review the security configuration of Kubernetes components
  (etcd, kubelet, kubedns, kubeapi)
---
# Find A Secret Directly In etcd

Run etcdctl inside the etcd pod with the health check certificate, list the etcd members and find the key of a Secret.

The task and solution use a separate pinned kind cluster with one control plane node and one worker node. Run `astrona test` on this folder: `testing/verify-start.sh` checks that every outcome fails on the starting state, then `solution/apply.sh` applies the reference solution and every outcome must pass.
