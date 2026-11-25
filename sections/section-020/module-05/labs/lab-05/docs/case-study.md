---
exam_objectives:
- Use CIS benchmark to review the security configuration of Kubernetes components
  (etcd, kubelet, kubedns, kubeapi)
---
# Starting Environment

The lab VM runs a one-node Kubernetes cluster built with kubeadm, the standard tool that installs a cluster on a Linux machine. The node `astro-ats-031-lab-020-05-05` is the control plane and also runs the pods. The `starfleet-031-020-05-05` namespace runs two `probe` replicas behind the `probe` Service and a `shuttle` client pod. The systemd unit files of the kubelet on the node have mode `644`, and certificate rotation is turned off. A copy of the original kubelet configuration is in `/opt/training/backup/kubelet-config.yaml` on the node.

Find the systemd unit files of the kubelet, restrict their mode, and turn client certificate rotation back on in the effective kubelet configuration.
