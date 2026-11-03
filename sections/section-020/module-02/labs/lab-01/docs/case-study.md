---
draft: true
exam_objectives:
- Use CIS benchmark to review the security configuration of Kubernetes components
  (etcd, kubelet, kubedns, kubeapi)
---
# Starting Environment

The kind cluster has two healthy probe replicas, a `shuttle` client pod and one control plane node that runs with the kubeadm defaults. No kube-bench result has been collected yet. The kube-bench image is preloaded on both nodes.
