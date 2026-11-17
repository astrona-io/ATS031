---
exam_objectives:
- Use CIS benchmark to review the security configuration of Kubernetes components
  (etcd, kubelet, kubedns, kubeapi)
---
# Starting Environment

The kind cluster has one control plane node and one worker node. The `starfleet-031-020-02-04` namespace runs two `probe` replicas behind the `probe` Service and a `shuttle` client pod. The `kube-bench` image `docker.io/aquasec/kube-bench:v0.10.6` is already loaded on both nodes. The ConfigMap `audit-request` in the `starfleet-031-020-02-04` namespace names the benchmark edition under the key `benchmark`. No kube-bench Job exists.

Run kube-bench with only the `etcd` target and a benchmark edition chosen with `--benchmark`, as a Job on the control plane node.
