---
exam_objectives:
- Use CIS benchmark to review the security configuration of Kubernetes components
  (etcd, kubelet, kubedns, kubeapi)
---
# Starting Environment

The lab VM runs a one-node Kubernetes cluster built with kubeadm, the standard tool that installs a cluster on a Linux machine. The node `astro-ats-031-lab-020-05-03` is the control plane and also runs the pods. The `starfleet-031-020-05-03` namespace runs two `probe` replicas behind the `probe` Service and a `shuttle` client pod. The file `/var/lib/kubelet/config.yaml` on the node sets `authorization.mode: Webhook`. A copy of the kubelet files is in `/opt/training/backup` on the node.

Find why the kubelet uses a weaker authorization mode than its configuration file says, remove the overriding flag and prove the effective value.
