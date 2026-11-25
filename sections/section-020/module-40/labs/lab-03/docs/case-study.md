---
exam_objectives:
- Use CIS benchmark to review the security configuration of Kubernetes components
  (etcd, kubelet, kubedns, kubeapi)
---
# Starting Environment

The lab VM runs a one-node Kubernetes cluster built with kubeadm, the standard tool that installs a cluster on a Linux machine. The node `astro-ats-031-lab-020-04-03` is the control plane and also runs the pods. The `starfleet-031-020-04-03` namespace runs two `probe` replicas behind the `probe` Service and a `shuttle` client pod. etcd runs as a static pod on the control plane node. Someone turned off client certificate authentication for the client and the peer ports of etcd. A copy of the etcd manifest from before that change is in `/opt/training/backup/etcd.yaml` on the control plane node.

Turn client certificate authentication on again for the client and peer ports of etcd, and prove that a request without a certificate is refused.
