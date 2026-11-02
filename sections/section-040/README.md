---
draft: true
exam_objectives:
- Protect node metadata and endpoints
---
# Protect node metadata and endpoints

A workload with no Kubernetes permissions can still reach a node metadata service or a management port and obtain authority that RBAC never granted. This section teaches which node-local endpoints carry authority, which network paths a policy covers and which it does not, and how to restrict and verify a pod's access with an egress allow-list.

## Learning Path

1. Protect Node Metadata And Management Endpoints: the landing page and the playground.
2. Endpoints That Carry Authority
3. Network Paths To A Metadata-Style Endpoint
4. Restrict The Pod And Verify The Boundary
5. Summary, then the ten-question knowledge check.

The parts carry the hands-on steps. Each lab follows the part that practises its skill. The playground is a private `kind` cluster with Kubernetes v1.35; launch it from the landing page and keep it running while you read.

## Learning Outcomes

- Name the node-local endpoints that carry authority: the cloud metadata service, the kubelet API and the container runtime socket.
- Explain why the identity of a node differs from the identity of a workload, and why RBAC does not cover a metadata service.
- Read the kubelet authentication and authorization settings from a running node, and find pods that mount host paths or use the host network.
- Show with requests from two namespaces that a pod can reach a metadata-style endpoint, and restrict it with an egress allow-list.
- Explain what a NetworkPolicy does not cover, and name provider-specific protections that complement it.
