---
draft: true
exam_objectives:
- Protect node metadata and endpoints
---
# Protect Node Endpoints And The Runtime

Besides the metadata address, a node exposes the kubelet application programming interface (API) on port 10250, sometimes a read-only port 10255, and the socket of the container runtime. A pod can reach the first two over the network, and it can reach the third if a volume gives it the file. Each of them can leak data or give control of the node. Kubernetes RBAC covers none of them in the usual way.

This module shows the exposure from inside a pod, closes the network paths with a NetworkPolicy, explains what the node identity may and may not do, and finds the pods that carry a runtime socket mount or use the host network. It ends with the controls that live outside the cluster and that no NetworkPolicy can replace.

## Learning objectives

After this module you can:

- Show with requests from a pod which kubelet ports answer, and explain what status codes 401, 403 and 200 mean for the kubelet.
- Block pod access to the kubelet ports with an `ipBlock` rule that keeps DNS and Services working.
- Explain what the node authorizer and the `NodeRestriction` admission plugin allow a node credential to do.
- Find pods that mount the runtime socket or a host directory, or that use the host network or run privileged.
- Name provider and host controls that complement NetworkPolicy.

## Before you start

You need Kubernetes basics, `kubectl`, and the NetworkPolicy rules from the first section of this course. The module has six parts. The first shows the kubelet ports from a pod. The second blocks them. The third explains node identity. The fourth and fifth find pods that expose the runtime or bypass policy. The sixth is reading only and covers controls outside the cluster.

Your playground is a `kind` cluster running Kubernetes v1.35 with Calico, which enforces NetworkPolicy. It has one control plane node and one worker node. The setup opens the kubelet read-only port 10255 on the worker on purpose, so that you can see what an exposed port gives away. It has these objects:

| Namespace | Object | What it is |
| --- | --- | --- |
| `metadata-stub` | `fake-imds` pod | A fake metadata server on the host network of the worker, listening on `169.254.169.254` port 80 |
| `metadata-stub` | `control` pod | A client pod that no policy selects, used as a control |
| `starfleet` | `probe` Deployment and Service, `shuttle` pod | A web server and a client pod |
| `starfleet` | `cri-helper` pod | Mounts the directory `/run/containerd` from the node |
| `outpost` | `probe` Deployment and Service, `drifter` pod | A web server and a client pod |
| `outpost` | `runtime-peek` pod | Mounts the container runtime socket from the node |
| `outpost` | `log-reader` pod | Mounts `/var/log` from the node |
| `dock` | `probe` Deployment and Service, `tender` pod | A web server and a client pod |
| `dock` | `net-tool` pod | Uses the host network |

The client pods run the `curl` command. No NetworkPolicy exists when the playground starts. `kubectl` already points at the playground cluster. Launch your playground now and keep it running while you read:

<!-- astrona:playground -->
