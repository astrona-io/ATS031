---
exam_objectives:
- Use CIS benchmark to review the security configuration of Kubernetes components
  (etcd, kubelet, kubedns, kubeapi)
---
# Starting Environment

The lab VM runs a one-node Kubernetes cluster built with kubeadm, the standard tool that installs a cluster on a Linux machine. The node `astro-ats-031-lab-020-03-06` is the control plane and also runs the pods. The `starfleet-031-020-03-06` namespace runs two `probe` replicas behind the `probe` Service and a `shuttle` client pod. The controller manager and the scheduler run with the profiling endpoint on (the default). Some files in `/etc/kubernetes/manifests` have mode `644`.

Disable profiling on the controller manager and the scheduler, and restrict the modes of the control plane manifest files.
