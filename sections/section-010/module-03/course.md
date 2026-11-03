---
draft: true
exam_objectives:
- Use Network security policies to restrict cluster level access
---
# Select Peers And Ports Precisely

Most mistakes in NetworkPolicy tasks are selector mistakes. A policy that selects the wrong peer either blocks a path the application needs or opens a path an attacker can use. A peer is an entry in the `from` or `to` list of a rule that says which pods, namespaces or IP address ranges the rule applies to. This module covers every peer form and every port form, with a request test for each.

A NetworkPolicy is a Kubernetes object that selects pods and lists the connections they may receive or make. The network plugin, here Calico, enforces it. The module teaches you to read and write the fields exactly, and to prove the effect with an allowed and a denied request.

## Learning objectives

After this module you can:

- Allow traffic from a pod in another namespace using the `kubernetes.io/metadata.name` label.
- Tell a combined `namespaceSelector` and `podSelector` entry from two separate list entries.
- Use `ipBlock` with `except` to allow a CIDR range and carve out one address.
- Use `ports`, `protocol` and `endPort`, and select pods by named port.

## Before you start

You need pods, namespaces, labels, Services and the commands `kubectl apply`, `kubectl get`, `kubectl label` and `kubectl exec`. You also need to know that a policy isolates the pods it selects and that policies add up. The module has six parts. The first recaps selectors and namespace labels. The second writes cross-namespace ingress. The third compares one list entry with two. The fourth covers `ipBlock`. The fifth covers ports. The sixth shows how policies behave with Services and replicas.

Your playground is a `kind` cluster running Kubernetes v1.35 with the Calico network plugin, which enforces NetworkPolicy. No NetworkPolicy exists yet. Namespaces carry only the label that the cluster sets automatically.

| Namespace | Pod or Service | What it is |
| --- | --- | --- |
| `starfleet`, `outpost` | `probe` Deployment, two pods, label `app: probe` | A small web server that listens on port 8080 |
| `starfleet`, `outpost` | `probe` Service | Port 80, forwards to port 8080 of the `probe` pods |
| `starfleet`, `outpost` | `shuttle` and `drifter` pods, labels `app: shuttle` and `app: drifter` | Client pods with `wget` |
| `dock` | `shuttle` pod, label `app: shuttle` | A client pod with `wget` |
| `dock` | `telemetry` pod, label `app: telemetry` | Listens on TCP port 9000 (named `feed`) and UDP port 9001 (named `pulse`) and answers every message |

`kubectl` already points at the playground cluster. Launch your playground now and keep it running while you read:

<!-- astrona:playground -->
