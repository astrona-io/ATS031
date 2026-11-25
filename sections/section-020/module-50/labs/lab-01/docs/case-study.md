---
exam_objectives:
- Use CIS benchmark to review the security configuration of Kubernetes components
  (etcd, kubelet, kubedns, kubeapi)
---
# Starting Environment

The lab VM runs a one-node Kubernetes cluster built with kubeadm, the standard tool that installs a cluster on a Linux machine. The node `astro-ats-031-lab-020-05-01` is the control plane and also runs the pods. The `starfleet-031-020-05-01` namespace runs two `probe` replicas behind the `probe` Service and a `shuttle` client pod. The kubelet on the node accepts anonymous requests and allows every request (`AlwaysAllow`). A copy of the original kubelet configuration is in `/opt/training/backup/kubelet-config.yaml` on the node.

Turn off anonymous requests to the kubelet API, switch the kubelet to Webhook authorization, and prove that an anonymous request is refused.
