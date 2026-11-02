---
draft: true
exam_objectives:
- Use Network security policies to restrict cluster level access
---
# Restrict Pod Traffic With NetworkPolicy

By default, every pod in a Kubernetes cluster can send a request to every other pod, in every namespace. A compromised pod can therefore scan and attack all other workloads. A NetworkPolicy is a Kubernetes object that selects pods and lists the network connections those pods may receive or make. All other connections to and from the selected pods are dropped.

A NetworkPolicy does nothing on its own. The Kubernetes API server (`kube-apiserver`) stores the object, and the cluster's network plugin (the Container Network Interface, CNI, plugin) turns it into packet filtering rules on each node. If the plugin does not implement NetworkPolicy, the object is accepted and has no effect.

This module teaches you to write policies that allow exactly one caller, to allow the egress a client needs (including DNS), and to prove with real requests that a policy works.

## Learning objectives

After this module you can:

- Explain which pods a policy isolates, in which direction, and how several policies combine.
- Write an ingress policy that allows one labelled peer and denies all others, including a peer in another namespace.
- Write an egress policy that allows DNS and one application dependency and blocks everything else.
- Explain why `namespaceSelector` and `podSelector` in one peer entry differ from two separate peer entries.
- Test a policy with an allowed request and a denied request, and tell a timeout from a refused connection.

## Before you start

You need Kubernetes basics: pods, namespaces, labels, selectors, Services, and the commands `kubectl get`, `kubectl apply` and `kubectl exec`. The module has four parts. The first explains isolation and the evaluation rules. The second writes an ingress policy. The third writes an egress policy with DNS. The fourth covers default-deny policies and troubleshooting.

Your playground is a `kind` cluster running Kubernetes v1.35 with the Calico network plugin, which enforces NetworkPolicy. It has these workloads:

| Namespace | Pod or Service | What it is |
| --- | --- | --- |
| `starfleet` | `probe` Deployment, two pods, label `app: probe` | A small web server that listens on port 8080 |
| `starfleet` | `probe` Service | Port 80, forwards to port 8080 of the `probe` pods |
| `starfleet` | `shuttle` pod, label `app: shuttle` | A client pod with `wget` |
| `outpost` | `drifter` pod, label `app: drifter` | A client pod with `wget` in another namespace |

`kubectl` already points at the playground cluster. Launch your playground now and keep it running while you read:

<!-- astrona:playground -->
