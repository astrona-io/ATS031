---
exam_objectives:
- Use CIS benchmark to review the security configuration of Kubernetes components
  (etcd, kubelet, kubedns, kubeapi)
---
# Starting Environment

The kind cluster has one control plane node and one worker node. The `starfleet-031-020-05-04` namespace runs two `probe` replicas behind the `probe` Service and a `shuttle` client pod. The kubelet on the worker node serves the read-only port `10255` and accepts TLS 1.0. A copy of the original kubelet configuration is in `/opt/training/backup/kubelet-config.yaml` on the worker node.

Close the plain HTTP read-only port of the kubelet and raise the lowest TLS version it accepts, then prove both from a pod and from the effective configuration.
