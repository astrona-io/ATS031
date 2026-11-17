---
exam_objectives:
- Use CIS benchmark to review the security configuration of Kubernetes components
  (etcd, kubelet, kubedns, kubeapi)
---
# Starting Environment

The kind cluster has one control plane node and one worker node. The `starfleet-031-020-01-04` namespace runs two `probe` replicas behind the `probe` Service and a `shuttle` client pod. The kubelet on the worker node runs with a setting that is not in its configuration file. The file `/var/lib/kubelet/config.yaml` on the worker has mode `644`.

Read the effective kubelet settings of the worker node through `configz`, record three of them, and restrict the mode of the kubelet configuration file.
