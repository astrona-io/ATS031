---
draft: true
exam_objectives:
- Use CIS benchmark to review the security configuration of Kubernetes components
  (etcd, kubelet, kubedns, kubeapi)
---
# Review Kubernetes Components With The CIS Benchmark

A Kubernetes cluster has many security settings that are not safe by default: the API server flags, the etcd data store, the kubelet on every node, and the permissions of the files that hold them. The Center for Internet Security (CIS) Kubernetes Benchmark is a published list of recommended settings for these components. You review a cluster by comparing its real settings with that list, and you fix what the list marks as a risk.

`kube-bench` is an open source tool that runs the benchmark checks against a node and prints a result for each one. The tool only reports. You still decide whether a finding is a real risk, change the setting, and prove that the cluster still works.

This module teaches you to find the files and flags the benchmark checks, to read a check and the setting behind it, to review the kubelet, and to correct one API server finding without stopping the cluster.

## Learning objectives

After this module you can:

- Explain how the CIS benchmark is organised and which component each section covers.
- Find the manifests, configuration files and certificates of a kubeadm cluster on a node.
- Read a `kube-bench` check (its audit, test and remediation) and run the same audit by hand.
- Review the effective kubelet configuration and the permissions of its files.
- Correct an API server flag in the static pod manifest, wait for the API server to return, and verify the new value.

## Before you start

You need Kubernetes basics: pods, namespaces, the control plane and `kubectl`. The module has four parts. The first maps the benchmark to the files of a kubeadm cluster. The second reads checks and audits the API server and etcd. The third reviews the kubelet. The fourth corrects a finding and records it.

Your playground is a `kind` cluster running Kubernetes v1.35 with one control plane node and one worker node. A kind node is a container that runs the kubelet and the control plane as a normal kubeadm node does. The `starfleet` namespace holds the `probe` Deployment (two pods), the `probe` Service and the `shuttle` client pod. Commands for the nodes start with `podman exec` and name the node container of this playground. `kubectl` already points at the cluster.

Launch your playground now and keep it running while you read:

<!-- astrona:playground -->
