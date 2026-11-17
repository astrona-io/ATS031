---
exam_objectives:
- Use CIS benchmark to review the security configuration of Kubernetes components
  (etcd, kubelet, kubedns, kubeapi)
---
# Starting Environment

The kind cluster has one control plane node and one worker node. The `starfleet-031-020-05-01` namespace runs two `probe` replicas behind the `probe` Service and a `shuttle` client pod. The kubelet on the worker node accepts anonymous requests and allows every request (`AlwaysAllow`). A copy of the original kubelet configuration is in `/opt/training/backup/kubelet-config.yaml` on the worker node.

Turn off anonymous requests to the kubelet API, switch the kubelet to Webhook authorization, and prove that an anonymous request is refused.
