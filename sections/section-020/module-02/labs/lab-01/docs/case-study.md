---
exam_objectives:
- Use CIS benchmark to review the security configuration of Kubernetes components
  (etcd, kubelet, kubedns, kubeapi)
---
# Starting Environment

The lab VM runs a one-node Kubernetes cluster built with kubeadm, the standard tool that installs a cluster on a Linux machine. The node `astro-ats-031-lab-020-02-01` is the control plane and also runs the pods. The `starfleet-031-020-02-01` namespace runs two `probe` replicas behind the `probe` Service and a `shuttle` client pod. The `kube-bench` image `docker.io/aquasec/kube-bench:v0.10.6` is already loaded on both nodes. The control plane node runs with the kubeadm defaults. No kube-bench result has been collected.

Run kube-bench for the control plane with JSON output, filter the failing API server checks and record exactly that list.
