---
draft: true
exam_objectives:
- Use Network security policies to restrict cluster level access
---
# Policy For Real Cluster Traffic And Troubleshooting

A policy that allows only the application connection breaks the application. Real workloads also need name resolution, access to the Kubernetes API server and health checks from the node. A NetworkPolicy is a Kubernetes object that selects pods and lists the connections they may receive or make, and the network plugin enforces it. This module covers the traffic that every real cluster needs, the traffic that policy cannot see, and a fixed method to test, audit and repair a policy set.

## Learning objectives

After this module you can:

- Allow DNS to CoreDNS on UDP and TCP port 53 and egress to the API server.
- Explain how kubelet probes and node traffic interact with policy in the network plugin used here.
- State what NetworkPolicy does not cover: `hostNetwork` pods, node traffic, application-layer rules and logging.
- Troubleshoot a deny with a fixed method (labels, selectors, `policyTypes`, network plugin) and audit the policies in a cluster.

## Before you start

You need to know how to write ingress and egress rules, peers and ports, and how default-deny policies isolate a namespace. The module has five parts. The first allows DNS. The second reaches the API server and other dependencies. The third covers probes, `hostNetwork` and node traffic. The fourth builds a test matrix. The fifth audits and repairs a broken policy set.

Your playground is a `kind` cluster running Kubernetes v1.35 with the Calico network plugin, which enforces NetworkPolicy. It already contains a policy set that does not work:

| Namespace | Pod or Service | What it is |
| --- | --- | --- |
| `starfleet` | `probe` Deployment, two pods, and `probe` Service | A web server on port 8080 behind a Service on port 80 |
| `starfleet` | `scout` pod, label `app: scout` | Resolves a name, calls the `probe` Service and lists pods through the API server with its ServiceAccount |
| `starfleet` | `beacon` pod, label `app: beacon` | Runs with `hostNetwork: true` and listens on node port 19099 |
| `outpost` | `drifter` pod, label `app: drifter` | A client pod with `wget`; no policy selects it |

The policies in `starfleet` are `default-deny-all`, `scout-egress`, `scout-to-probe` and `probe-ingress`. They contain several mistakes, which the parts find one by one. The `scout` pod has a test script, `python /app/check.py`, that prints one result for each of its three needs: `dns`, `probe` and `api`.

`kubectl` already points at the playground cluster. Launch your playground now and keep it running while you read:

<!-- astrona:playground -->
