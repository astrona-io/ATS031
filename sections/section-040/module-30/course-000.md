# Protect Node Endpoints And The Runtime

A pod can reach more of its node than most people expect. The metadata address of a cloud machine is one path. The node also has the kubelet, the agent that starts and watches pods. The kubelet serves an application programming interface (API) on port 10250, and sometimes a read-only port 10255 as well. A third path is the socket of the container runtime, a file on the node that controls every container on it.

A pod reaches the two kubelet ports over the network. It reaches the runtime socket only if a volume puts that file inside the container. Each path can leak data or give an attacker control of the node. Kubernetes role-based access control (RBAC), the rules that decide what a user may do through the Kubernetes API, does not cover any of them in the usual way.

This module shows each exposure from inside a pod and then closes it. A NetworkPolicy closes the network paths. Admission control keeps dangerous pods out. Some controls live outside the cluster, and no NetworkPolicy can replace them.

## What you will learn

After this module, you can:

- show with requests from a pod which kubelet ports answer, and explain what the status codes 401, 403 and 200 mean for the kubelet;
- block pod access to the kubelet ports with an `ipBlock` rule that keeps DNS and Services working;
- explain what the node authorizer and the `NodeRestriction` admission plugin allow a node credential to do;
- find pods that mount the runtime socket or a host directory, and pods that use the host network or run privileged;
- name the cloud provider and host controls that add to NetworkPolicy.

## How the module is laid out

You start with **The Kubelet API From A Pod**, which sends requests to both kubelet ports from an ordinary client pod. **Restrict Reachability To Node Ports** then closes that path with a NetworkPolicy. **Node Identity And NodeRestriction** explains what a stolen node credential can and cannot do.

The next two pages look at pods that reach the node by other routes. **Runtime Socket And hostPath Exposure** finds pods that mount the runtime socket. **hostNetwork And Privileged Pods Bypass Policy** shows a pod that a NetworkPolicy does not restrict, and how to stop such pods at creation. **Controls Outside The Cluster** closes the module. It is reading only and covers the controls of the node, the cloud account and the network.

A lab follows each hands-on page, so you can practise the skill right away.

## Before you start

You should know the Kubernetes basics: pods, namespaces, labels, Services and `kubectl`. You should also know how a NetworkPolicy selects pods and how an `ipBlock` rule with an `except` list allows a range of addresses but leaves some out.

## Your playground

Your playground is a `kind` cluster that runs Kubernetes v1.35 with the Calico network plugin. Calico enforces NetworkPolicy, so every policy you write has a real effect. The cluster has one control plane node and one worker node.

The setup changes the worker node on purpose, so that you can see what an exposed node gives away:

- It opens the kubelet read-only port 10255 on the worker.
- It adds the address `169.254.169.254` to the worker, for the fake metadata server.
- It tells Calico to accept traffic from pods to the addresses of the node, so the paths to the node can be tested.

The cluster already runs these workloads:

| Namespace | Object | What it is |
| --- | --- | --- |
| `metadata-stub` | `fake-imds` pod, label `app: fake-imds` | A fake metadata server on the host network of the worker. It listens on `169.254.169.254` port 80 and runs code from the `fake-imds-code` ConfigMap. Every value it returns is invented |
| `metadata-stub` | `control` pod, label `app: control` | A client pod that no policy selects, used as a control |
| `starfleet` | `probe` Deployment, one pod, label `app: probe` | A small web server that listens on port 8080 |
| `starfleet` | `probe` Service | Port 80, forwards to port 8080 of the `probe` pod |
| `starfleet` | `shuttle` pod, label `app: shuttle` | A client pod |
| `starfleet` | `agent` pod, labels `app: agent` and `role: cloud-agent` | A client pod |
| `starfleet` | `cri-helper` pod, label `app: cri-helper` | Runs as root and mounts the directory `/run/containerd` from the node |
| `outpost` | `probe` Deployment, one pod, label `app: probe` | A small web server that listens on port 8080 |
| `outpost` | `probe` Service | Port 80, forwards to port 8080 of the `probe` pod |
| `outpost` | `drifter` pod, label `app: drifter` | A client pod |
| `outpost` | `runtime-peek` pod, label `app: runtime-peek` | Runs as root and mounts the runtime socket `/run/containerd/containerd.sock` from the node |
| `outpost` | `log-reader` pod, label `app: log-reader` | Mounts `/var/log` from the node, read-only |
| `dock` | `probe` Deployment, one pod, label `app: probe` | A small web server that listens on port 8080 |
| `dock` | `probe` Service | Port 80, forwards to port 8080 of the `probe` pod |
| `dock` | `tender` pod, label `app: tender` | A client pod |
| `dock` | `net-tool` pod, label `app: net-tool` | A pod that uses the host network |

Every pod except `fake-imds` and the `probe` pods runs the `curl` image, so you can send requests from it. No NetworkPolicy exists when the playground starts.

`kubectl` already points at the playground cluster. Start your playground now and keep it running while you read:

<!-- astrona:playground -->
