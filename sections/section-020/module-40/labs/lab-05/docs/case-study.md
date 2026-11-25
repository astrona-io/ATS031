---
exam_objectives:
- Use CIS benchmark to review the security configuration of Kubernetes components
  (etcd, kubelet, kubedns, kubeapi)
---
# Starting Environment

The lab VM runs a one-node Kubernetes cluster built with kubeadm, the standard tool that installs a cluster on a Linux machine. The node `astro-ats-031-lab-020-04-05` is the control plane and also runs the pods. The `starfleet-031-020-04-05` namespace runs two `probe` replicas behind the `probe` Service and a `shuttle` client pod. etcd runs as a static pod on the control plane node. A Secret called `relay-token` exists in one namespace of the cluster. The lab does not tell you which namespace.

Run etcdctl inside the etcd pod with the health check certificate, list the etcd members and find the key of a Secret.
