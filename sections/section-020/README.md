---
draft: true
exam_objectives:
- Use CIS benchmark to review the security configuration of Kubernetes components
  (etcd, kubelet, kubedns, kubeapi)
---
# Use CIS benchmark to review the security configuration of Kubernetes components (etcd, kubelet, kubedns, kubeapi)

A security review asks whether the cluster meets the CIS Kubernetes Benchmark. The answer depends on reading the settings the components really use, not the files that look relevant. This section teaches how the benchmark is organised, how to audit the control plane and the kubelet with `kube-bench` as reference and manual checks as practice, and how to correct a finding safely and record it.

## Learning Path

1. Review Kubernetes Components With The CIS Benchmark: the landing page and the playground.
2. The Benchmark And Where The Settings Live
3. Read A Check: kube-bench And The Manual Audit
4. Review The Kubelet: Effective Configuration And File Permissions
5. Correct A Finding Safely And Record It
6. Summary, then the ten-question knowledge check.

The parts carry the hands-on steps. Each lab follows the part that practises its skill. The playground is a private `kind` cluster with Kubernetes v1.35; launch it from the landing page and keep it running while you read.

## Learning Outcomes

- Explain how the CIS benchmark is organised and which component each section covers.
- Find the manifests, configuration files and certificates of a kubeadm cluster on a node.
- Read a `kube-bench` check (its audit, test and remediation) and run the same audit by hand.
- Review the effective kubelet configuration and the permissions of its files.
- Correct an API server flag in the static pod manifest, wait for the API server to return, and verify the new value.
