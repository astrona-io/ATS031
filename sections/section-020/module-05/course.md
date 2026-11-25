# Harden The kubelet And CoreDNS, Then Remediate End To End

The kubelet is the agent that runs on every node. It starts the containers of the pods on its node, and it serves an HTTPS interface that can list pods, read logs and run commands inside containers. If that interface accepts unauthenticated or unauthorized requests, an attacker who reaches the node network controls every pod on the node. The Center for Internet Security (CIS) Kubernetes Benchmark checks the kubelet on every node for this reason.

This module teaches you to find where the kubelet reads its settings, to set authentication, authorization, ports and Transport Layer Security (TLS) options, to review the CoreDNS component that provides cluster DNS, and to run the complete remediation loop for a mixed list of findings: audit, change, restart, audit again and compare.

## Learning objectives

After this module you can:

- Edit `/var/lib/kubelet/config.yaml` safely, restart the kubelet and confirm the effective configuration.
- Turn anonymous authentication off, set the authorization mode to `Webhook`, close the read-only port and set TLS and rotation options.
- Explain `protectKernelDefaults`, `streamingConnectionIdleTimeout` and the kubelet file permission checks, and say what the node must have before you turn `protectKernelDefaults` on.
- Review the CoreDNS Deployment and its Corefile for security-relevant settings.
- Run the whole loop for a mixed set of findings and record the results from before and after.

## Before you start

You need Kubernetes basics: nodes, pods, Services, DNS in a cluster and `kubectl`. The module has six parts. The first covers where the kubelet gets its settings. The second covers authentication and authorization. The third covers ports and TLS. The fourth covers the remaining checks and the file permissions. The fifth reviews CoreDNS. The sixth runs the full remediation loop.

Your playground is one virtual machine (VM) that runs a single-node Kubernetes v1.35 cluster built with kubeadm, the standard tool that installs a cluster on a Linux machine. The node `astro-ats-031-playground-020-05` is the control plane and also runs your pods, so the kubelet you harden runs on the same machine as the API server. The `starfleet` namespace holds the `probe` Deployment, the `probe` Service and the `shuttle` client pod. The playground weakens the kubelet on purpose: anonymous authentication is on, the authorization mode is `AlwaysAllow`, the read-only port `10255` is open and two files are wider than the benchmark allows. A copy of the original kubelet configuration is in `/opt/training/backup` on the node.

You work in a shell on the node. Open it with `astrona ssh astro-ats-031-playground-020-05`. You log in as the user `student`, which has `sudo` and a kubeconfig for the cluster, so `kubectl` already points at the cluster. Commands that read or change node files start with `sudo`.

Launch your playground now and keep it running while you read:

<!-- astrona:playground -->
