---
exam_objectives:
- Use CIS benchmark to review the security configuration of Kubernetes components
  (etcd, kubelet, kubedns, kubeapi)
---
# Starting Environment

The lab VM runs a one-node Kubernetes cluster built with kubeadm, the standard tool that installs a cluster on a Linux machine. The node `astro-ats-031-lab-020-03-04` is the control plane and also runs the pods. The `starfleet-031-020-03-04` namespace runs two `probe` replicas behind the `probe` Service and a `shuttle` client pod. The API server allows every request, and an extra RBAC binding grants read access to anonymous requests. The lab does not tell you the name of the binding.

Restore the `Node,RBAC` authorization mode of the API server and remove the RBAC binding that lets anonymous requests read the cluster.
