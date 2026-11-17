---
exam_objectives:
- Use CIS benchmark to review the security configuration of Kubernetes components
  (etcd, kubelet, kubedns, kubeapi)
---
# Recover A Broken Controller Manager Static Pod

Find why the kube-controller-manager static pod keeps failing, repair its manifest without a second static pod, and keep the manifest file restricted.

The task and solution use a separate pinned kind cluster with one control plane node and one worker node. Run `astrona test` on this folder: `testing/verify-start.sh` checks that every outcome fails on the starting state, then `solution/apply.sh` applies the reference solution and every outcome must pass.
