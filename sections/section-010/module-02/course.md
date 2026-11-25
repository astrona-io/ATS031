# Build Default-Deny Baselines For Namespaces

A namespace without a NetworkPolicy accepts every connection to and from every pod in it. A NetworkPolicy is a Kubernetes object that selects pods and lists the connections those pods may receive (ingress) or make (egress). Until one exists, nothing is blocked.

A baseline is the first NetworkPolicy you put in a namespace. It selects all pods and allows nothing, so every connection needs an allowance from a later policy. The Certified Kubernetes Security Specialist (CKS) exam asks for this order again and again: deny first, allow second.

The policy itself does not filter traffic. The network plugin of the cluster, here Calico, reads the policy and enforces it on each node. In this module you build the three baselines (deny ingress, deny egress, deny both), see what each one breaks, and add allow rules on top in a safe order.

## What you will learn

After this module, you can:

- write default-deny ingress, default-deny egress and combined policies with an empty `podSelector`;
- predict the effect of each baseline on a running workload before you apply it;
- apply a baseline to several namespaces and add allow rules on top in a safe order;
- explain why policies are additive and why the core NetworkPolicy API has no deny rule.

## How the module is laid out

You start with **Why A Baseline Comes First**, which shows the open cluster with real requests and explains what isolation changes. **Deny All Ingress** then stops all incoming connections in one namespace. **Deny All Egress And Its Side Effects** stops outgoing connections and shows why DNS breaks first.

**Combine Baselines With Allow Rules** puts a baseline for both directions in place and opens one path on top of it. **Baselines Across Many Namespaces** closes the module and rolls the same baseline out to several namespaces from one file.

## Before you start

You should know pods, namespaces, labels and Services. You should also be able to use `kubectl apply`, `kubectl get` and `kubectl exec`. Finally, you should know one rule: a pod that no policy selects accepts all traffic.

## Your playground

Your playground is a `kind` cluster that runs Kubernetes v1.35 with the Calico network plugin. Calico enforces NetworkPolicy, so every policy you write has a real effect. No NetworkPolicy exists yet. Each of the three namespaces runs the same workloads:

| Namespace | Pod or Service | What it is |
| --- | --- | --- |
| `starfleet`, `outpost`, `dock` | `probe` Deployment, two pods, label `app: probe` | A small web server that listens on port 8080 |
| `starfleet`, `outpost`, `dock` | `probe` Service | Port 80, forwards to port 8080 of the `probe` pods |
| `starfleet`, `outpost`, `dock` | `shuttle` pod, label `app: shuttle` | A client pod with `wget` |

`kubectl` already points at the playground cluster. Start your playground now and keep it running while you read:

<!-- astrona:playground -->
