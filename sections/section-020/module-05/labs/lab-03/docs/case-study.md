---
exam_objectives:
- Use CIS benchmark to review the security configuration of Kubernetes components
  (etcd, kubelet, kubedns, kubeapi)
---
# Starting Environment

The kind cluster has one control plane node and one worker node. The `starfleet-031-020-05-03` namespace runs two `probe` replicas behind the `probe` Service and a `shuttle` client pod. The file `/var/lib/kubelet/config.yaml` on the worker node sets `authorization.mode: Webhook`. A copy of the kubelet files is in `/opt/training/backup` on the worker node.

Find why the kubelet uses a weaker authorization mode than its configuration file says, remove the overriding flag and prove the effective value.
