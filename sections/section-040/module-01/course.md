---
draft: true
exam_objectives:
- Protect node metadata and endpoints
---
# Protect Node Metadata And Management Endpoints

A cluster node is more than a place where pods run. It is a machine with its own services: a kubelet that manages the pods, a container runtime with a control socket, and, on a cloud provider, a metadata service that hands out information and credentials to anything on the machine that asks. These endpoints are not part of the Kubernetes API, so Kubernetes RBAC does not govern them. A pod that can reach one of them may obtain more authority than its ServiceAccount ever granted.

This module teaches you to find the endpoints that carry authority, to see which network paths a pod can use to reach them, and to restrict and verify a pod's access with a NetworkPolicy. The playground models a cloud metadata endpoint with an ordinary web server pod, because the playground has no cloud provider. The network technique is real. The cloud-specific protections are explained but cannot be exercised here.

## Learning objectives

After this module you can:

- Name the node-local endpoints that carry authority: the cloud metadata service, the kubelet API and the container runtime socket.
- Explain why the identity of a node differs from the identity of a workload, and why RBAC does not cover a metadata service.
- Read the kubelet authentication and authorization settings from a running node, and find pods that mount host paths or use the host network.
- Show with requests from two namespaces that a pod can reach a metadata-style endpoint, and restrict it with an egress allow-list.
- Explain what a NetworkPolicy does not cover, and name provider-specific protections that complement it.

## Before you start

You need Kubernetes basics, `kubectl`, and the NetworkPolicy rules from the first section of this course. The module has three parts. The first covers the endpoints and the authority behind them. The second covers the network paths and shows the unrestricted baseline. The third restricts access and verifies the result.

Your playground is a `kind` cluster running Kubernetes v1.35 with Calico, which enforces NetworkPolicy. It has these objects:

| Namespace | Object | What it is |
| --- | --- | --- |
| `starfleet` | `probe` Deployment (two pods) and `probe` Service | A web server on pod port 8080, Service port 80 |
| `starfleet` | `shuttle` pod | A busybox client that you will restrict |
| `outpost` | `drifter` pod | A busybox client that stays unrestricted and acts as a control |

`kubectl` already points at the playground cluster. Launch your playground now and keep it running while you read:

<!-- astrona:playground -->
