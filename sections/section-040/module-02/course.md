---
draft: true
exam_objectives:
- Protect node metadata and endpoints
---
# Block The Cloud Metadata Endpoint

Every major cloud provider runs an instance metadata service (IMDS) on the link-local address `169.254.169.254`. A process on the virtual machine, and by default every pod on it, can ask that address for facts about the machine and for temporary cloud credentials. Stopping pods from reaching this address is a common task in the Certified Kubernetes Security Specialist exam, and it takes a few lines of NetworkPolicy once you know which form to use.

This module builds a realistic target in the playground. A small web server called `fake-imds` listens on `169.254.169.254` on the worker node and answers with clearly fake data, so every exercise uses the real address and the real network path. You will block the address for a whole namespace, allow it again for one labelled pod, learn which mistakes leave it open, and check coverage across namespaces.

## Learning objectives

After this module you can:

- Explain what the metadata service returns, why the credentials it hands out are dangerous, and what changes between its first and second versions.
- Block `169.254.169.254/32` for all pods in a namespace with an `ipBlock` and an `except` entry, while other egress keeps working.
- Allow the address for pods that carry one label, and explain why that label must be controlled.
- Name the policy mistakes that leave the address open, including a pod that uses the host network.
- Prove the result with requests from allowed and denied pods, and find namespaces that have no egress policy.

## Before you start

You need Kubernetes basics, `kubectl`, and the NetworkPolicy rules from the first section of this course: a policy selects pods, policies add up, and a pod that no policy selects for egress is not restricted. The module has six parts. The first explains the metadata service and its cloud-specific details and has no commands. The second inspects the playground target and the network path to it. The third blocks the address with an `ipBlock` rule. The fourth adds a selective allow. The fifth covers the mistakes that leave the address open. The sixth checks every namespace.

Your playground is a `kind` cluster running Kubernetes v1.35 with Calico, which enforces NetworkPolicy. It has one control plane node and one worker node. It has these objects:

| Namespace | Object | What it is |
| --- | --- | --- |
| `metadata-stub` | `fake-imds` pod | A fake metadata server on the host network of the worker node, listening on `169.254.169.254` port 80 |
| `metadata-stub` | `control` pod | A client pod that no policy selects, used as a control |
| `starfleet` | `probe` Deployment and Service | A web server on pod port 8080, Service port 80 |
| `starfleet` | `shuttle` pod | A client pod without special labels |
| `starfleet` | `agent` pod | A client pod labelled `role=cloud-agent` |
| `outpost` | `probe` Deployment and Service | The same web server in this namespace |
| `outpost` | `drifter` pod | A client pod |
| `dock` | `probe` Deployment and Service | The same web server in this namespace |
| `dock` | `tender` pod | A client pod |

The client pods run the `curl` command. No NetworkPolicy exists in any namespace when the playground starts. `kubectl` already points at the playground cluster. Launch your playground now and keep it running while you read:

<!-- astrona:playground -->
