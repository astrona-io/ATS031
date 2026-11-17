---
exam_objectives:
- Use CIS benchmark to review the security configuration of Kubernetes components
  (etcd, kubelet, kubedns, kubeapi)
---
# Run The etcd Checks With A Pinned Benchmark Edition

Run kube-bench with only the `etcd` target and a benchmark edition chosen with `--benchmark`, as a Job on the control plane node.

The task and solution use a separate pinned kind cluster with one control plane node and one worker node. Run `astrona test` on this folder: `testing/verify-start.sh` checks that every outcome fails on the starting state, then `solution/apply.sh` applies the reference solution and every outcome must pass.
