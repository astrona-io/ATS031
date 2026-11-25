---
exam_objectives:
- Use CIS benchmark to review the security configuration of Kubernetes components
  (etcd, kubelet, kubedns, kubeapi)
---
# Remove Write Access To The CoreDNS Configuration

Find the RBAC grant that lets a workload service account change the CoreDNS ConfigMap, remove it, and switch the Corefile to verified pod records without breaking name resolution.

The task and solution use a separate pinned kind cluster with one control plane node and one worker node. Run `astrona test` on this folder: `testing/verify-start.sh` checks that every outcome fails on the starting state, then `solution/apply.sh` applies the reference solution and every outcome must pass.
