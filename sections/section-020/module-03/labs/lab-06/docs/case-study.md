---
exam_objectives:
- Use CIS benchmark to review the security configuration of Kubernetes components
  (etcd, kubelet, kubedns, kubeapi)
---
# Starting Environment

The kind cluster has one control plane node and one worker node. The `starfleet-031-020-03-06` namespace runs two `probe` replicas behind the `probe` Service and a `shuttle` client pod. The controller manager and the scheduler run with the profiling endpoint on (the default). Some files in `/etc/kubernetes/manifests` have mode `644`.

Disable profiling on the controller manager and the scheduler, and restrict the modes of the control plane manifest files.
