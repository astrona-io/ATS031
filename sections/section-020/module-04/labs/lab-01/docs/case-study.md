---
draft: true
exam_objectives:
- Use CIS benchmark to review the security configuration of Kubernetes components
  (etcd, kubelet, kubedns, kubeapi)
---
# Starting Environment

The isolated environment has two healthy probe replicas, an internal Service, two client Pods and the Secret `launch-code`. The API server has no encryption configuration.

Enable encryption at rest for Secrets and prove it with etcd.
