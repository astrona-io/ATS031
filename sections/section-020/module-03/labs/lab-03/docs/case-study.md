---
exam_objectives:
- Use CIS benchmark to review the security configuration of Kubernetes components
  (etcd, kubelet, kubedns, kubeapi)
---
# Starting Environment

The kind cluster has one control plane node and one worker node. The `starfleet-031-020-03-03` namespace runs two `probe` replicas behind the `probe` Service and a `shuttle` client pod. The kube-controller-manager static pod fails to start after a manual edit of its manifest. A copy of the manifest from before the edit is in `/opt/training/backup/kube-controller-manager.yaml` on the control plane node.

Find why the kube-controller-manager static pod keeps failing, repair its manifest without a second static pod, and keep the manifest file restricted.
