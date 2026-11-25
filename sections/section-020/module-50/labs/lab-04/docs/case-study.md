---
exam_objectives:
- Use CIS benchmark to review the security configuration of Kubernetes components
  (etcd, kubelet, kubedns, kubeapi)
---
# Starting Environment

The lab VM runs a one-node Kubernetes cluster built with kubeadm, the standard tool that installs a cluster on a Linux machine. The node `astro-ats-031-lab-020-05-04` is the control plane and also runs the pods. The `starfleet-031-020-05-04` namespace runs two `probe` replicas behind the `probe` Service and a `shuttle` client pod. The kubelet on the node serves the read-only port `10255` and accepts TLS 1.0. A copy of the original kubelet configuration is in `/opt/training/backup/kubelet-config.yaml` on the node.

Close the plain HTTP read-only port of the kubelet and raise the lowest TLS version it accepts, then prove both from a pod and from the effective configuration.
