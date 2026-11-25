---
exam_objectives:
- Use CIS benchmark to review the security configuration of Kubernetes components
  (etcd, kubelet, kubedns, kubeapi)
---
# Starting Environment

The lab VM runs a one-node Kubernetes cluster built with kubeadm, the standard tool that installs a cluster on a Linux machine. The node `astro-ats-031-lab-020-02-04` is the control plane and also runs the pods. The `starfleet-031-020-02-04` namespace runs two `probe` replicas behind the `probe` Service and a `shuttle` client pod. The `kube-bench` image `docker.io/aquasec/kube-bench:v0.10.6` is already loaded on the node. The ConfigMap `audit-request` in the `starfleet-031-020-02-04` namespace names the benchmark edition under the key `benchmark`. No kube-bench Job exists.

Run kube-bench with only the `etcd` target and a benchmark edition chosen with `--benchmark`, as a Job on the control plane node.
