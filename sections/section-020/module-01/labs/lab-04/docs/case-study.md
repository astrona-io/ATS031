---
exam_objectives:
- Use CIS benchmark to review the security configuration of Kubernetes components
  (etcd, kubelet, kubedns, kubeapi)
---
# Starting Environment

The lab VM runs a one-node Kubernetes cluster built with kubeadm, the standard tool that installs a cluster on a Linux machine. The node `astro-ats-031-lab-020-01-04` is the control plane and also runs the pods. The `starfleet-031-020-01-04` namespace runs two `probe` replicas behind the `probe` Service and a `shuttle` client pod. The kubelet on the node runs with a setting that is not in its configuration file. The file `/var/lib/kubelet/config.yaml` on the node has mode `644`.

Read the effective kubelet settings of the node through `configz`, record three of them, and restrict the mode of the kubelet configuration file.
