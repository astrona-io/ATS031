---
exam_objectives:
- Use CIS benchmark to review the security configuration of Kubernetes components
  (etcd, kubelet, kubedns, kubeapi)
---
# Record A Manual Audit Of The API Server And etcd

Read four benchmark settings from the running API server and etcd processes and from the node, and record the values in a ConfigMap.

The task and solution use a separate pinned kind cluster with one control plane node and one worker node. Run `astrona test` on this folder: `testing/verify-start.sh` checks that every outcome fails on the starting state, then `solution/apply.sh` applies the reference solution and every outcome must pass.
