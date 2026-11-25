---
exam_objectives:
- Use CIS benchmark to review the security configuration of Kubernetes components
  (etcd, kubelet, kubedns, kubeapi)
---
# Starting Environment

The lab VM runs a one-node Kubernetes cluster built with kubeadm, the standard tool that installs a cluster on a Linux machine. The node `astro-ats-031-lab-020-03-01` is the control plane and also runs the pods. The `starfleet-031-020-03-01` namespace runs two `probe` replicas behind the `probe` Service and a `shuttle` client pod. An audit policy is staged in `/opt/training/audit-policy.yaml` on the control plane node. No component uses it yet, and the API server writes no audit log.

Enable audit logging on the API server with a staged policy, set the log retention, and prove that the API server writes an event.
