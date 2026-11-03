---
draft: true
exam_objectives:
- Protect node metadata and endpoints
---
# Protect node metadata and endpoints

A workload with no Kubernetes permissions can still reach a node metadata service or a management port and obtain authority that RBAC never granted. This section teaches which node-local endpoints carry authority, which network paths a policy covers and which it does not, and how to restrict and verify a pod's access with an egress allow-list.

## Learning Path

1. Protect Node Metadata And Management Endpoints: the first module, with the landing page, three parts, one lab and the knowledge check.
2. Block The Cloud Metadata Endpoint: the metadata service, an `ipBlock` with `except`, a selective allow for one labelled pod, policy pitfalls and a coverage check. Two labs and a knowledge check.
3. Protect Node Endpoints And The Runtime: the kubelet ports, node identity and `NodeRestriction`, runtime socket and `hostPath` exposure, host network pods, and controls outside the cluster. Two labs and a knowledge check.
4. Capstone: Protect The Node, one graded lab that combines the metadata block, the kubelet port block and the removal of a runtime socket mount.

Each module has a summary and a ten-question knowledge check. Each lab follows the part that practises its skill. Every module playground is a private `kind` cluster with Kubernetes v1.35 and Calico; launch it from the landing page and keep it running while you read.

## Learning Outcomes

- Name the node-local endpoints that carry authority: the cloud metadata service, the kubelet API and the container runtime socket.
- Explain why the identity of a node differs from the identity of a workload, and why RBAC does not cover a metadata service.
- Read the kubelet authentication and authorization settings from a running node, and find pods that mount host paths or use the host network.
- Show with requests from two namespaces that a pod can reach a metadata-style endpoint, and restrict it with an egress allow-list.
- Explain what a NetworkPolicy does not cover, and name provider-specific protections that complement it.
- Block the metadata address for a namespace with an `ipBlock` and an `except` entry, and open it for one labelled pod with a second policy.
- Explain why two separate deny-list policies on the same pods cancel each other, and put every exception in one list.
- Restrict pod access to the kubelet ports and read the node authorization settings.
- Find pods that mount the container runtime socket or use the host network, and explain why a pod policy does not cover host network pods.
- Name the controls that live outside the cluster, such as metadata service settings and node identity configuration at a cloud provider.
