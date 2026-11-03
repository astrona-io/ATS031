---
draft: true
exam_objectives:
- Use CIS benchmark to review the security configuration of Kubernetes components
  (etcd, kubelet, kubedns, kubeapi)
---
# Starting Environment

The isolated environment has a control plane node, a worker node, two healthy probe replicas and two client Pods. Two kubelet files have mode 644 and three kubelet settings fail the benchmark.

Remediate the five findings.
