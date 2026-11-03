---
draft: true
exam_objectives:
- Use CIS benchmark to review the security configuration of Kubernetes components
  (etcd, kubelet, kubedns, kubeapi)
---
# Use CIS benchmark to review the security configuration of Kubernetes components (etcd, kubelet, kubedns, kubeapi)

A security review asks whether the cluster meets the CIS Kubernetes Benchmark. The answer depends on reading the settings the components really use, not the files that look relevant. This section teaches how the benchmark is organised, how to audit the control plane and the kubelet with `kube-bench` as reference and manual checks as practice, and how to correct a finding safely and record it.

## Learning Path

1. Review Kubernetes Components With The CIS Benchmark: how the benchmark is organised, how to read a check and how to correct a finding on the API server.
2. Run kube-bench And Read Its Output: the tool that runs the checks, its targets and versions, and how to judge a result and a false finding.
3. Harden The API Server And Control Plane Components: the API server flags, admission, audit logging and the files of the control plane.
4. Review etcd Security Configuration: the etcd client and peer TLS flags, the data directory, a direct query with `etcdctl` and encryption at rest.
5. Harden The kubelet And CoreDNS, Then Remediate End To End: kubelet authentication, authorization and ports, the CoreDNS review and a full remediation.
6. Capstone lab: remediate findings on the API server, etcd and the kubelet in one cluster and record the evidence.

Each module ends with a summary and a ten-question knowledge check. Each lab follows the part that practises its skill. Every module has a private `kind` playground with Kubernetes v1.35; launch it from the landing page and keep it running while you read. A `kind` node is a container that shares the kernel of the host, so the playgrounds cannot test every kernel-level or host-level setting, and each part says where a check does not apply.

## Learning Outcomes

- Explain how the CIS benchmark is organised and which component each section covers.
- Find the manifests, configuration files and certificates of a kubeadm cluster on a node.
- Read a `kube-bench` check (its audit, test and remediation) and run the same audit by hand.
- Review the effective kubelet configuration and the permissions of its files.
- Correct an API server flag in the static pod manifest, wait for the API server to return, and verify the new value.
- Review the etcd TLS flags and data directory permissions, read stored data with `etcdctl`, and enable encryption at rest for Secrets.
- Close anonymous access and open authorization on the kubelet, and fix its ports, certificate rotation and TLS settings.
- Review the CoreDNS Deployment, its Corefile and its permissions.
- Combine these fixes on one cluster and record the evidence of each change.
