---
exam_objectives:
- Use CIS benchmark to review the security configuration of Kubernetes components
  (etcd, kubelet, kubedns, kubeapi)
---
# Starting Environment

The lab VM runs a one-node Kubernetes cluster built with kubeadm, the standard tool that installs a cluster on a Linux machine. The node `astro-ats-031-lab-020-03-05` is the control plane and also runs the pods. The `starfleet-031-020-03-05` namespace runs two `probe` replicas behind the `probe` Service and a `shuttle` client pod. The API server runs without the `NodeRestriction` admission plugin.

Enable the NodeRestriction admission plugin on the API server, then use the node kubelet credentials to prove that a kubelet can no longer set a `node-restriction.kubernetes.io/` label.
