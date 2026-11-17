---
exam_objectives:
- Use CIS benchmark to review the security configuration of Kubernetes components
  (etcd, kubelet, kubedns, kubeapi)
---
# Starting Environment

The kind cluster has one control plane node and one worker node. The `starfleet-031-020-01-02` namespace runs two `probe` replicas behind the `probe` Service and a `shuttle` client pod. Some files in `/etc/kubernetes` and `/etc/kubernetes/pki` on the control plane node have mode `644`. The lab does not tell you which ones.

Find the kubeconfig files and private key files on the control plane node that have a wider mode than the benchmark allows, and restrict them.
