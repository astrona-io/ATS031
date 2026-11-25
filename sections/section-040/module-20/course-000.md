# Block The Cloud Metadata Endpoint

Every major cloud provider runs an instance metadata service (IMDS) for each virtual machine. It is an HTTP server on the link-local address `169.254.169.254`. A process on the virtual machine can ask this address for facts about the machine and for temporary cloud credentials. By default, every pod on the machine can ask it too.

Stopping pods from reaching this address is a common task in the Certified Kubernetes Security Specialist (CKS) exam. The fix is a NetworkPolicy of a few lines, once you know which form to use. A NetworkPolicy is the Kubernetes object that selects a group of pods and lists the connections those pods may make or receive.

In this module, the playground gives you a realistic target. A small web server called `fake-imds` listens on `169.254.169.254` on the worker node and answers with clearly fake data. So every exercise uses the real address and the real network path, without any real credentials.

## What you will learn

After this module, you can:

- explain what the metadata service returns, why the credentials it hands out are dangerous, and what changes between its first and second versions;
- block `169.254.169.254/32` for all pods in a namespace with an `ipBlock` and an `except` entry, while other egress keeps working;
- allow the address for pods that carry one label, and explain why that label must be controlled;
- name the policy mistakes that leave the address open, including a pod that uses the host network;
- prove the result with requests from allowed and denied pods, and find namespaces that have no egress policy.

## How the module is laid out

You start with **What The Metadata Service Hands Out**, which explains what the service returns and how the cloud providers differ. This page has no commands. **The Playground Metadata Server** then looks at the fake server and the network path from a pod to it, and records what every pod can read before any policy exists.

**Block With An ipBlock Except Rule** closes the address for a whole namespace. **Default Deny Plus A Selective Allow** opens it again for one labelled pod. **Policy Pitfalls For The Metadata Address** shows the mistakes that leave the address open, and **Verify Coverage Across Namespaces** checks every namespace and closes the gaps.

A lab follows each hands-on page, so you can practise the skill right away.

## Before you start

You should know the Kubernetes basics: pods, namespaces, labels, selectors and Services. You should also be able to use `kubectl get`, `kubectl apply` and `kubectl exec`.

You also need three NetworkPolicy rules. A policy selects pods in its own namespace. When several policies select the same pod, the pod may use any traffic that one of them allows. A pod that no policy selects for egress (outgoing traffic) can send traffic anywhere.

## Your playground

Your playground is a `kind` cluster that runs Kubernetes v1.35 with the Calico network plugin. Calico enforces NetworkPolicy, so every policy you write has a real effect. The cluster has one control plane node and one worker node.

When the playground starts, the setup adds the address `169.254.169.254/32` to the worker node. It also sets the Calico option `defaultEndpointToHostAction` to `Accept`, so pods can reach addresses that belong to the node. The cluster then runs these objects:

| Namespace | Object | What it is |
| --- | --- | --- |
| `metadata-stub` | `fake-imds-code` ConfigMap | The Python code of the fake metadata server |
| `metadata-stub` | `fake-imds` pod, label `app: fake-imds` | A fake metadata server on the host network of the worker node, listening on `169.254.169.254` port 80 |
| `metadata-stub` | `control` pod, label `app: control` | A client pod that no policy selects, used as a control |
| `starfleet` | `probe` Deployment, one pod, label `app: probe` | A small web server that listens on port 8080 |
| `starfleet` | `probe` Service | Port 80, forwards to port 8080 of the `probe` pod |
| `starfleet` | `shuttle` pod, label `app: shuttle` | A client pod without special labels |
| `starfleet` | `agent` pod, labels `app: agent` and `role: cloud-agent` | A client pod that plays a cloud agent |
| `outpost` | `probe` Deployment and Service | The same web server, one pod, Service port 80 |
| `outpost` | `drifter` pod, label `app: drifter` | A client pod |
| `dock` | `probe` Deployment and Service | The same web server, one pod, Service port 80 |
| `dock` | `tender` pod, label `app: tender` | A client pod |

The client pods run the `curl` command. No NetworkPolicy exists in any namespace when the playground starts. `kubectl` already points at the playground cluster. Start your playground now and keep it running while you read:

<!-- astrona:playground -->
