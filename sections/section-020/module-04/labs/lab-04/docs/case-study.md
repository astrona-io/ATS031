---
exam_objectives:
- Use CIS benchmark to review the security configuration of Kubernetes components
  (etcd, kubelet, kubedns, kubeapi)
---
# Starting Environment

The lab VM runs a one-node Kubernetes cluster built with kubeadm, the standard tool that installs a cluster on a Linux machine. The node `astro-ats-031-lab-020-04-04` is the control plane and also runs the pods. The `starfleet-031-020-04-04` namespace runs two `probe` replicas behind the `probe` Service and a `shuttle` client pod. etcd runs as a static pod on the control plane node. Someone opened the mode of the etcd data directory.

Find the etcd data directory from the running process, restrict its mode to 700, and record which user runs etcd.
