---
draft: true
exam_objectives:
- Use CIS benchmark to review the security configuration of Kubernetes components
  (etcd, kubelet, kubedns, kubeapi)
---
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

Your playground is a `kind` cluster running Kubernetes v1.35 with one control plane node and one worker node. A kind node is a container that runs the kubelet and the control plane as a normal kubeadm node does. etcd runs as a static pod on the control plane node. The `starfleet` namespace holds the `probe` Deployment, the `probe` Service, the `shuttle` client pod and a Secret named `launch-code`. The playground sets the permissions of the etcd data directory wider than the benchmark allows, on purpose.

Commands for the node start with `podman exec` and name the node container of this playground. `kubectl` already points at the cluster. A kind node is a container on a shared host, so some findings differ from a dedicated virtual machine. Where this matters, the part says so.

Launch your playground now and keep it running while you read:

<!-- astrona:playground -->
