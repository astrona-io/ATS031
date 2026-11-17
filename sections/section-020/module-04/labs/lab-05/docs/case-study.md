---
exam_objectives:
- Use CIS benchmark to review the security configuration of Kubernetes components
  (etcd, kubelet, kubedns, kubeapi)
---
# Starting Environment

The kind cluster has one control plane node and one worker node. The `starfleet-031-020-04-05` namespace runs two `probe` replicas behind the `probe` Service and a `shuttle` client pod. etcd runs as a static pod on the control plane node. A Secret called `relay-token` exists in one namespace of the cluster. The lab does not tell you which namespace.

Run etcdctl inside the etcd pod with the health check certificate, list the etcd members and find the key of a Secret.
