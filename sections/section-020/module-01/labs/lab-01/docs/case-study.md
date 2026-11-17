---
exam_objectives:
- Use CIS benchmark to review the security configuration of Kubernetes components
  (etcd, kubelet, kubedns, kubeapi)
---
# Starting Environment

The kind cluster has one control plane node and one worker node. The `starfleet-031-020-01-01` namespace runs two `probe` replicas behind the `probe` Service and a `shuttle` client pod. The kube-scheduler static pod runs with `--bind-address=0.0.0.0`, so its secure port `10259` listens on every address of the control plane node.

Correct the kube-scheduler `--bind-address` finding in its static pod manifest, check that the new process listens only on the loopback address, and record the change.
