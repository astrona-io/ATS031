# Harden The API Server And Control Plane Components

Most failing checks of a Center for Internet Security (CIS) Kubernetes Benchmark run belong to the control plane. The API server is the front door of the cluster. It decides who may connect, what each user may do and which requests are recorded. The controller manager and the scheduler run beside it, and their manifests and settings have checks of their own.

On a kubeadm cluster the control plane components are static pods: pods that the kubelet starts from manifest files on the node, without the API server. You change a component by editing its manifest file. A mistake in that file can stop the API server, and then `kubectl` no longer works. This module teaches the safe way to edit, the flags the benchmark checks, and how to prove after each change that the component runs with the new value.

## Learning objectives

After this module you can:

- Edit a static pod manifest through a copy, and recover when the component does not start.
- Set and verify the authentication and authorization flags of the API server.
- Explain the admission plugins `NodeRestriction` and `AlwaysPullImages` and verify which plugins run.
- Enable audit logging with a policy file, the log flags and the volume mounts they need.
- Set and verify the profiling, TLS and service account flags.
- Apply the controller manager and scheduler settings and fix the permissions of manifests.

## Before you start

You need Kubernetes basics and the knowledge that a `kube-bench` run reports failing checks with a remediation text. The module has six parts. The first covers static pods and safe editing. The second covers authentication and authorization flags. The third covers admission plugins. The fourth covers audit logging. The fifth covers profiling, TLS and service account flags. The sixth covers the controller manager, the scheduler and file permissions.

Your playground is one virtual machine (VM) that runs a single-node Kubernetes v1.35 cluster built with kubeadm, the standard tool that installs a cluster on a Linux machine. The node `astro-ats-031-playground-020-03` is the control plane and also runs your pods. The API server runs with some deliberately weak settings: profiling is at its default value and no audit policy is set. Three control plane manifests have mode `644`.

An audit policy file is staged on the node at `/opt/training/audit-policy.yaml`, but nothing uses it. A copy of every original manifest is in `/opt/training/backup`. The `starfleet` namespace holds the `probe` Deployment, the `probe` Service and the `shuttle` client pod.

You open a shell on the node with `astrona ssh astro-ats-031-playground-020-03`. You log in as the `student` user, which can run commands as root with `sudo` and already has `kubectl` set up for the cluster.

Launch your playground now and keep it running while you read:

<!-- astrona:playground -->
