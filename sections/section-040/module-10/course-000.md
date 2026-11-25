# Protect Node Metadata And Management Endpoints

A cluster node is more than a place where pods run. It is a machine with its own services. The kubelet, the agent that manages the pods on the node, has its own API. The container runtime, the program that starts and stops containers, has a control socket. On a cloud provider, a metadata service hands out information and credentials to anything on the machine that asks.

These endpoints are not part of the Kubernetes API, so Kubernetes role-based access control (RBAC) does not govern them. RBAC is the system that decides what a user or a ServiceAccount may do through the Kubernetes API. A pod that can reach one of these endpoints may get more authority than its ServiceAccount ever granted.

In this module, you find the endpoints that carry authority, see which network paths a pod can use to reach them, and restrict and verify a pod's access with a NetworkPolicy. The playground has no cloud provider, so it models a cloud metadata endpoint with an ordinary web server pod. The network technique is real. The cloud-specific protections are explained, but you cannot try them here.

## What you will learn

After this module, you can:

- name the node-local endpoints that carry authority: the cloud metadata service, the kubelet API and the container runtime socket;
- explain why the identity of a node differs from the identity of a workload, and why RBAC does not cover a metadata service;
- read the kubelet authentication and authorization settings from a running node, and find pods that mount host paths or use the host network;
- show with requests from two namespaces that a pod can reach a metadata-style endpoint, and restrict it with an egress allow-list;
- explain what a NetworkPolicy does not cover, and name provider-specific protections that work together with it.

## How the module is laid out

You start with **Endpoints That Carry Authority**, which describes the endpoints, the authority behind them and how to inspect the kubelet and host paths. **Network Paths To A Metadata-Style Endpoint** then shows which paths a NetworkPolicy can see, and proves that a pod can reach an unprotected endpoint today. **Restrict The Pod And Verify The Boundary** closes that path with an egress allow-list and proves the result with three requests.

A lab follows the part on network paths and the part on restricting the pod, so you can practise each skill right away.

## Before you start

You should know the Kubernetes basics and be able to use `kubectl`. You should also know how a NetworkPolicy works. A NetworkPolicy is the Kubernetes object that selects a group of pods and lists the connections they may receive (ingress) or make (egress). Once a policy selects a pod for a direction, every connection in that direction that no policy allows is dropped.

## Your playground

Your playground is a `kind` cluster that runs Kubernetes v1.35 with the Calico network plugin, on one control plane node and one worker node. Calico enforces NetworkPolicy, so every policy you write has a real effect. The cluster already runs these objects:

| Namespace | Object | What it is |
| --- | --- | --- |
| `starfleet` | `probe` Deployment, two pods, labels `app: probe` and `release: probe` | A small Python web server that listens on pod port 8080 |
| `starfleet` | `probe` Service | Port 80, forwards to port 8080 of the `probe` pods |
| `starfleet` | `probe-code` ConfigMap | The server code that the `probe` pods run |
| `starfleet` | `shuttle` pod, label `app: shuttle` | A busybox client pod with `wget`, the pod you restrict |
| `outpost` | `drifter` pod, label `app: drifter` | A busybox client pod with `wget`, which stays unrestricted as a control |

`kubectl` already points at the playground cluster. Start your playground now and keep it running while you read:

<!-- astrona:playground -->
