---
draft: true
exam_objectives:
- Use CIS benchmark to review the security configuration of Kubernetes components
  (etcd, kubelet, kubedns, kubeapi)
---
# Starting Environment

The isolated environment has a control plane node, a worker node, two healthy probe replicas, an internal Service, two client Pods and the Secret `launch-code`. The benchmark review found six findings across the API server, etcd and the kubelet.

Fix them and record the evidence.
