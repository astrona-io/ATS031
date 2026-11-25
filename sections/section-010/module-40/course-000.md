# Policy For Real Cluster Traffic And Troubleshooting

A policy that allows only the application connection breaks the application. Real workloads need more than that one connection. They also need name resolution, access to the Kubernetes API server and health checks from the node.

A NetworkPolicy is the Kubernetes object that selects a group of pods and lists the connections those pods may receive or make. The network plugin of the cluster reads the policy and enforces it. This module covers the traffic that every real cluster needs, the traffic that a policy cannot see, and a fixed method to test, audit and repair a set of policies.

## What you will learn

After this module, you can:

- allow DNS to CoreDNS on UDP and TCP port 53, and allow egress to the API server;
- explain how kubelet probes and node traffic interact with policy in the network plugin used here;
- state what NetworkPolicy does not cover: `hostNetwork` pods, node traffic, application-layer rules and logging;
- troubleshoot a denied connection with a fixed method (labels, selectors, `policyTypes`, network plugin) and audit the policies in a cluster.

## How the module is laid out

You start with **DNS And CoreDNS Egress**, which restores name lookups for a pod under an egress baseline. **Egress To The API Server And Other Dependencies** then allows the API server and services outside the cluster, which have no labels to select. **Probes, hostNetwork And Node Traffic** shows the traffic that pod policy does not reach.

**Test Matrix For A Policy Set** builds a table of the paths that must work and the paths that must fail, and runs it with bounded requests. **Audit And Troubleshoot Policies** closes the module with a fixed method that finds and repairs the faults in a broken set of policies.

## Before you start

You should know how to write ingress and egress rules, peers and ports. You should also know how a default-deny policy isolates every pod in a namespace.

## Your playground

Your playground is a `kind` cluster that runs Kubernetes v1.35 with the Calico network plugin. Calico enforces NetworkPolicy, so every policy has a real effect. The cluster already contains a set of policies that does not work:

| Namespace | Pod or Service | What it is |
| --- | --- | --- |
| `starfleet` | `probe` Deployment, two pods, and `probe` Service | A web server on port 8080 behind a Service on port 80 |
| `starfleet` | `scout` pod, label `app: scout` | Resolves a name, calls the `probe` Service and lists pods through the API server with its ServiceAccount |
| `starfleet` | `beacon` pod, label `app: beacon` | Runs with `hostNetwork: true` and listens on node port 19099 |
| `outpost` | `drifter` pod, label `app: drifter` | A client pod with `wget`; no policy selects it |

The policies in `starfleet` are `default-deny-all`, `scout-egress`, `scout-to-probe` and `probe-ingress`. They contain several mistakes, and you find them one by one as you read. The `scout` pod has a test script, `python /app/check.py`. It prints one result for each of the three things the pod needs: `dns`, `probe` and `api`.

`kubectl` already points at the playground cluster. Start your playground now and keep it running while you read:

<!-- astrona:playground -->
