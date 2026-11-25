# Restrict Pod Traffic With NetworkPolicy

In a new Kubernetes cluster, every pod can send a request to every other pod, in every namespace. That is handy while you build, but it is a risk in production. If an attacker takes over one pod, they can reach and attack every other workload from there.

A NetworkPolicy is the Kubernetes object that closes this gap. It selects a group of pods and lists the connections those pods may receive or make. All other connections to and from those pods are dropped.

The policy does not filter traffic by itself. The Kubernetes API server (`kube-apiserver`) only stores it. The network plugin of the cluster, the Container Network Interface (CNI) plugin, reads the policy and turns it into packet filtering rules on each node. If the plugin does not support NetworkPolicy, the API server still accepts the policy, but nothing is blocked.

## What you will learn

After this module, you can:

- explain which pods a policy isolates, in which direction, and how several policies combine;
- write an ingress policy that lets one labelled pod in and keeps all others out, including pods in other namespaces;
- write an egress policy that allows DNS and one dependency, and blocks everything else;
- explain why `namespaceSelector` and `podSelector` in one peer entry differ from two separate peer entries;
- test a policy with one request that must pass and one that must fail, and tell a timeout from a refused connection.

## How the module is laid out

You start with **How NetworkPolicy Isolation Works**, which explains when a pod becomes isolated and how the rules of several policies add up. **Allow One Peer With An Ingress Policy** then lets a single caller in. **Restrict Egress And Allow DNS** controls what a pod may reach on the way out, without breaking name lookups. **Default Deny And Troubleshooting Policies** closes the module with deny-all policies and a method to find out why a connection fails.

A lab follows each part, so you can practise the skill right away.

## Before you start

You should know the Kubernetes basics: pods, namespaces, labels, selectors and Services. You should also be able to use `kubectl get`, `kubectl apply` and `kubectl exec`.

## Your playground

Your playground is a `kind` cluster that runs Kubernetes v1.35 with the Calico network plugin. Calico enforces NetworkPolicy, so every policy you write has a real effect. The cluster already runs these workloads:

| Namespace | Object | What it is |
| --- | --- | --- |
| `starfleet` | `probe` Deployment, two pods, label `app: probe` | A small web server that listens on port 8080 |
| `starfleet` | `probe` Service | Port 80, forwards to port 8080 of the `probe` pods |
| `starfleet` | `shuttle` pod, label `app: shuttle` | A client pod with `wget` |
| `outpost` | `drifter` pod, label `app: drifter` | A client pod with `wget`, in another namespace |

`kubectl` already points at the playground cluster. Start your playground now and keep it running while you read:

<!-- astrona:playground -->
