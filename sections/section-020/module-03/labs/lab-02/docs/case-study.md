---
exam_objectives:
- Use CIS benchmark to review the security configuration of Kubernetes components
  (etcd, kubelet, kubedns, kubeapi)
---
# Starting Environment

The lab VM runs a one-node Kubernetes cluster built with kubeadm, the standard tool that installs a cluster on a Linux machine. The node `astro-ats-031-lab-020-03-02` is the control plane and also runs the pods. The `starfleet-031-020-03-02` namespace runs two `probe` replicas behind the `probe` Service and a `shuttle` client pod. The API server runs with the profiling endpoint on (the default) and with `--tls-min-version=VersionTLS10`.

Turn off the profiling endpoint of the API server and raise its minimum TLS version, then prove both on the running API server.
