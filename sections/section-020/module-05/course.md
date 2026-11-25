# Harden The kubelet And CoreDNS, Then Remediate End To End

The kubelet is the agent that runs on every node. It starts the containers of the pods on its node. It also serves an HTTPS interface that can list pods, read logs and run commands inside containers. If that interface accepts requests without checking who sends them, an attacker who reaches the node network controls every pod on the node.

For this reason, the Center for Internet Security (CIS) Kubernetes Benchmark checks the kubelet on every node. The benchmark is a published list of security checks for a cluster. Cluster DNS (Domain Name System) needs a review too, because every pod uses it to find Services by name.

## What you will learn

After this module, you can:

- edit `/var/lib/kubelet/config.yaml` safely, restart the kubelet and confirm the effective configuration;
- turn anonymous authentication off, set the authorization mode to `Webhook`, close the read-only port and set Transport Layer Security (TLS) and certificate rotation options;
- explain `protectKernelDefaults`, `streamingConnectionIdleTimeout` and the kubelet file permission checks, and say what the node must have before you turn `protectKernelDefaults` on;
- review the CoreDNS Deployment and its Corefile for security-relevant settings;
- run the whole remediation loop for a mixed set of findings, and record the results from before and after.

## How the module is laid out

You start with **Kubelet Configuration Sources**, which shows where the kubelet reads its settings and how to change them without breaking the node. **Kubelet Authentication And Authorization** then closes anonymous access to the kubelet API. **Read-Only Port, Ports And TLS Settings** closes the port that needs no credentials and sets the TLS options. **Other Kubelet Checks** covers the kernel, timeout and file permission checks.

**Review CoreDNS (kube-dns)** moves from the kubelet to cluster DNS. **Remediate Findings End To End** closes the module: it runs the full loop of audit, change, restart, audit again and compare on a list of findings.

## Before you start

You need the Kubernetes basics: nodes, pods, Services, DNS in a cluster and `kubectl`.

## Your playground

Your playground is one virtual machine (VM) that runs a single-node Kubernetes v1.35 cluster. The cluster is built with kubeadm, the standard tool that installs a cluster on a Linux machine. The node `astro-ats-031-playground-020-05` is the control plane and also runs your pods. So the kubelet you harden runs on the same machine as the API server.

The playground weakens the kubelet on purpose, so that you have real findings to fix. A copy of the original kubelet configuration is in `/opt/training/backup` on the node.

| Place | Object | What it is |
| --- | --- | --- |
| `starfleet` namespace | `probe` Deployment and `probe` Service | A small web application to test that workloads still run |
| `starfleet` namespace | `shuttle` pod | A client pod to send requests from inside the cluster |
| `outpost` namespace | `drifter` pod | A client pod in another namespace |
| kubelet | anonymous authentication | Turned on |
| kubelet | authorization mode | Set to `AlwaysAllow` |
| kubelet | read-only port `10255` | Open |
| node files | two kubelet files | Their permissions are wider than the benchmark allows |

You work in a shell on the node. Open it with `astrona ssh astro-ats-031-playground-020-05`. You log in as the user `student`. This user has `sudo` and a kubeconfig for the cluster, so `kubectl` already points at the cluster. Commands that read or change node files start with `sudo`.

Start your playground now and keep it running while you read:

<!-- astrona:playground -->
