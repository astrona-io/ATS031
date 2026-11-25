# Harden The API Server And Control Plane Components

The Center for Internet Security (CIS) Kubernetes Benchmark is a list of security checks for a cluster. When you run it, most of the failing checks belong to the control plane. The API server is the front door of the cluster. It decides who may connect, what each user may do and which requests are recorded. The controller manager and the scheduler run beside it, and their manifests and settings have checks of their own.

On a kubeadm cluster, the control plane components are static pods. A static pod is a pod that the kubelet starts from a manifest file on the node, without the API server. You change a component by editing its manifest file. A mistake in that file can stop the API server, and then `kubectl` no longer works.

This module teaches the safe way to edit these files and the flags that the benchmark checks. It also shows how to prove after each change that the component runs with the new value.

## What you will learn

After this module, you can:

- edit a static pod manifest through a copy, and recover when the component does not start;
- set and verify the authentication and authorization flags of the API server;
- explain the admission plugins `NodeRestriction` and `AlwaysPullImages` and verify which plugins run;
- turn on audit logging with a policy file, the log flags and the volume mounts they need;
- set and verify the profiling, TLS and service account flags;
- apply the controller manager and scheduler settings and fix the permissions of manifests.

## How the module is laid out

You start with **Static Pods And Safe Editing**, which shows how the kubelet runs the control plane from files and how to change those files without breaking the cluster. **Authentication And Authorization Flags** then sets who may reach the API server and what they may do. **Admission Plugins** explains the plugins that check each request before the API server stores it.

**Audit Logging** adds a record of every request. **Profiling, TLS And Service Account Flags** reduces what the API server exposes and checks how it protects its connections and tokens. **Controller Manager, Scheduler And File Permissions** closes the module with the other two components and the file modes of the manifests.

## Before you start

You should know the Kubernetes basics: pods, namespaces, Services and `kubectl`. You should also know that a `kube-bench` run reports failing checks, each with a remediation text that says how to fix it.

## Your playground

Your playground is one virtual machine (VM) that runs a single-node Kubernetes v1.35 cluster. It was built with kubeadm, the standard tool that installs a cluster on a Linux machine. The node `astro-ats-031-playground-020-03` is the control plane and also runs your pods.

The API server runs with some weak settings on purpose: profiling is at its default value and no audit policy is set. Three control plane manifests have mode `644`. The node and the cluster hold these items:

| Place | Item | What it is |
| --- | --- | --- |
| Node | `/opt/training/audit-policy.yaml` | An audit policy file that nothing uses yet |
| Node | `/opt/training/backup` | A copy of every original control plane manifest |
| `starfleet` namespace | `probe` Deployment and `probe` Service | A small web workload |
| `starfleet` namespace | `shuttle` pod | A client pod |
| `outpost` namespace | `drifter` pod | A client pod in another namespace |

You open a shell on the node with `astrona ssh astro-ats-031-playground-020-03`. You log in as the `student` user. This user can run commands as root with `sudo` and already has `kubectl` set up for the cluster.

Start your playground now and keep it running while you read:

<!-- astrona:playground -->
