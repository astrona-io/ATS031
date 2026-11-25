# Review etcd Security Configuration

etcd is the key-value database where the Kubernetes API server stores every object of the cluster: pods, Deployments, RBAC rules and Secrets. Anyone who can read etcd can read every Secret. Anyone who can write to etcd can change the whole cluster without going through authentication, authorization or admission control.

For this reason, the Center for Internet Security (CIS) Kubernetes Benchmark gives etcd its own section. The benchmark is a list of checks that describes a secure configuration for each part of a cluster. In this module, you review etcd against these checks and fix what you find.

## What you will learn

After this module, you can:

- read the etcd static pod manifest and name the flags that the benchmark checks for etcd;
- verify that `--client-cert-auth` and `--peer-client-cert-auth` are `true`, and that `--auto-tls` and `--peer-auto-tls` are not enabled;
- set the permissions of the etcd data directory to mode `700` and explain the ownership recommendation;
- show that a client without a certificate cannot read etcd, and that a Secret is stored as plain text without an encryption configuration;
- enable encryption at rest with an `EncryptionConfiguration`, restart the API server safely and re-encrypt the existing Secrets.

## How the module is laid out

You start with **What Lives In etcd And Who Talks To It**, which shows what etcd stores, which ports it opens and which component connects to it. **Client And Peer TLS Flags** then reads the Transport Layer Security (TLS) flags in the etcd manifest and proves with a request what they do. **Data Directory Ownership And Permissions** checks who can read the files where etcd keeps its data.

**Query etcd With etcdctl** connects to etcd directly and shows what a client with a valid certificate can see. **Encryption At Rest Check** closes the module: you make the API server encrypt Secrets before it writes them to etcd, and you prove that it works.

A lab follows each part, so you can practise the skill right away.

## Before you start

You should know the Kubernetes basics: pods, namespaces, Secrets, static pods and `kubectl`. A static pod is a pod that the kubelet starts from a file on the node, not from the API server.

## Your playground

Your playground is one virtual machine (VM) that runs a single-node Kubernetes v1.35 cluster. The cluster was built with kubeadm, the standard tool that installs a cluster on a Linux machine. The node `astro-ats-031-playground-020-04` is the control plane, and it also runs your pods. etcd runs on it as a static pod, started from a file in `/etc/kubernetes/manifests`.

| Place | Object | What it is |
| --- | --- | --- |
| `starfleet` namespace | `probe` Deployment | An example workload |
| `starfleet` namespace | `probe` Service | The Service for the `probe` pods |
| `starfleet` namespace | `shuttle` pod | A client pod |
| `outpost` namespace | `drifter` pod | A client pod in another namespace |
| `starfleet` namespace | `launch-code` Secret | The Secret you look for in etcd |
| Node | `/var/lib/etcd` | The etcd data directory, set wider than the benchmark allows, on purpose |
| Node | `/opt/training/backup` | A copy of the original API server and etcd manifests |

You work in a shell on the node. Open it with `astrona ssh astro-ats-031-playground-020-04`. You log in as the user `student`, which has `sudo` and a kubeconfig file for the cluster. A kubeconfig file tells `kubectl` which cluster to use and which credentials to send, so `kubectl` already points at the cluster. Commands that read or change node files start with `sudo`.

Start your playground now and keep it running while you read:

<!-- astrona:playground -->
