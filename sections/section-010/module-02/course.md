---
draft: true
exam_objectives:
- Use Network security policies to restrict cluster level access
---
# Build Default-Deny Baselines For Namespaces

A namespace without a NetworkPolicy accepts every connection to and from every pod in it. A baseline is the first NetworkPolicy you put in a namespace: it selects all pods and allows nothing, so every connection must be allowed by a later policy. The Certified Kubernetes Security Specialist (CKS) exam asks for this order again and again: deny first, allow second.

A NetworkPolicy is a Kubernetes object that selects pods and lists the connections those pods may receive (ingress) or make (egress). The network plugin, here Calico, enforces it on each node. This module builds the three baselines (deny ingress, deny egress, deny both), shows what each one breaks, and adds allow rules on top in a safe order.

## Learning objectives

After this module you can:

- Write default-deny ingress, default-deny egress and combined policies with an empty `podSelector`.
- Predict the effect of each baseline on a running workload before you apply it.
- Apply a baseline to several namespaces and add allow rules on top in a safe order.
- Explain why policies are additive and why the core NetworkPolicy API has no deny rule.

## Before you start

You need pods, namespaces, labels, Services and the commands `kubectl apply`, `kubectl get` and `kubectl exec`. You also need to know that a pod which no policy selects accepts all traffic. The module has five parts. The first explains why the baseline comes first. The second denies ingress. The third denies egress and shows why DNS breaks. The fourth combines baselines with allow rules. The fifth rolls a baseline out to many namespaces.

Your playground is a `kind` cluster running Kubernetes v1.35 with the Calico network plugin, which enforces NetworkPolicy. No NetworkPolicy exists yet. Each of the three namespaces runs the same two workloads:

| Namespace | Pod or Service | What it is |
| --- | --- | --- |
| `starfleet`, `outpost`, `dock` | `probe` Deployment, two pods, label `app: probe` | A small web server that listens on port 8080 |
| `starfleet`, `outpost`, `dock` | `probe` Service | Port 80, forwards to port 8080 of the `probe` pods |
| `starfleet`, `outpost`, `dock` | `shuttle` pod, label `app: shuttle` | A client pod with `wget` |

`kubectl` already points at the playground cluster. Launch your playground now and keep it running while you read:

<!-- astrona:playground -->
