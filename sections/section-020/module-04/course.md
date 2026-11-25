# Review etcd Security Configuration

etcd is the key-value database where the Kubernetes API server stores every object of the cluster: pods, Deployments, RBAC rules and Secrets. Anyone who can read etcd can read every Secret, and anyone who can write to etcd can change the whole cluster without going through authentication, authorization or admission control. For this reason the Center for Internet Security (CIS) Kubernetes Benchmark gives etcd its own section.

This module teaches you to read the etcd static pod manifest and judge its Transport Layer Security (TLS) flags, to check the permissions of the data directory, to query etcd with `etcdctl` and see what is stored, and to turn on encryption at rest for Secrets and prove that it works.

## Learning objectives

After this module you can:

- Read the etcd static pod manifest and name the flags that the benchmark checks for etcd.
- Verify that `--client-cert-auth` and `--peer-client-cert-auth` are `true` and that `--auto-tls` and `--peer-auto-tls` are not enabled.
- Set the permissions of the etcd data directory to mode `700` and explain the ownership recommendation.
- Show that a client without a certificate cannot read etcd, and that a Secret is stored as plain text without an encryption configuration.
- Enable encryption at rest with an `EncryptionConfiguration`, restart the API server safely and re-encrypt the existing Secrets.

## Before you start

You need Kubernetes basics: pods, namespaces, Secrets, static pods and `kubectl`. The module has five parts. The first explains what etcd stores and which components talk to it. The second reads the TLS flags. The third covers the data directory. The fourth queries etcd with `etcdctl`. The fifth enables encryption at rest.

Your playground is one virtual machine (VM) that runs a single-node Kubernetes v1.35 cluster built with kubeadm, the standard tool that installs a cluster on a Linux machine. The node `astro-ats-031-playground-020-04` is the control plane and also runs your pods. etcd runs on it as a static pod, a pod that the kubelet starts from a file in `/etc/kubernetes/manifests`. The `starfleet` namespace holds the `probe` Deployment, the `probe` Service, the `shuttle` client pod and a Secret named `launch-code`. The playground sets the permissions of the etcd data directory wider than the benchmark allows, on purpose. A copy of the original API server and etcd manifests is in `/opt/training/backup` on the node.

You work in a shell on the node. Open it with `astrona ssh astro-ats-031-playground-020-04`. You log in as the user `student`, which has `sudo` and a kubeconfig for the cluster, so `kubectl` already points at the cluster. Commands that read or change node files start with `sudo`.

Launch your playground now and keep it running while you read:

<!-- astrona:playground -->
