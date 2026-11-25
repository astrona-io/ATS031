---
exam_objectives:
- Use CIS benchmark to review the security configuration of Kubernetes components
  (etcd, kubelet, kubedns, kubeapi)
---
# Starting Environment

The lab VM runs a one-node Kubernetes cluster built with kubeadm, the standard tool that installs a cluster on a Linux machine. The node `astro-ats-031-lab-020-01-03` is the control plane and also runs the pods. The `starfleet-031-020-01-03` namespace runs two `probe` replicas behind the `probe` Service and a `shuttle` client pod. The API server and etcd run with settings that this lab chose at start. Some differ from the kubeadm defaults, and the lab does not tell you which.

Read four benchmark settings from the running API server and etcd processes and from the node, and record the values in a ConfigMap.
