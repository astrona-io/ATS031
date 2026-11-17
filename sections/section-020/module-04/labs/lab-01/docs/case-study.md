---
exam_objectives:
- Use CIS benchmark to review the security configuration of Kubernetes components
  (etcd, kubelet, kubedns, kubeapi)
---
# Starting Environment

The kind cluster has one control plane node and one worker node. The `starfleet-031-020-04-01` namespace runs two `probe` replicas behind the `probe` Service and a `shuttle` client pod. etcd runs as a static pod on the control plane node. The Secret `launch-code` in the `starfleet-031-020-04-01` namespace holds the key `code` with the value `warp-nine-launch`. The API server has no encryption configuration, so etcd stores the value as plain text. A copy of the API server manifest is in `/opt/training/backup/kube-apiserver.yaml` on the control plane node.

Enable aescbc encryption at rest for Secrets on the API server, rewrite the existing Secrets and prove that etcd stores them encrypted.
