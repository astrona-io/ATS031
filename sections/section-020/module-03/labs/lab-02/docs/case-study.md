---
exam_objectives:
- Use CIS benchmark to review the security configuration of Kubernetes components
  (etcd, kubelet, kubedns, kubeapi)
---
# Starting Environment

The kind cluster has one control plane node and one worker node. The `starfleet-031-020-03-02` namespace runs two `probe` replicas behind the `probe` Service and a `shuttle` client pod. The API server runs with the profiling endpoint on (the default) and with `--tls-min-version=VersionTLS10`.

Turn off the profiling endpoint of the API server and raise its minimum TLS version, then prove both on the running API server.
