# Review Kubernetes Components With The CIS Benchmark

Many security settings in a Kubernetes cluster are not safe by default. This is true for the flags of the API server, the etcd data store, the kubelet on every node, and the permissions of the files that hold these settings. A reviewer needs a fixed list to compare the cluster against, or important settings get missed.

The Center for Internet Security (CIS) Kubernetes Benchmark is that list. It is a published document of recommended settings for each component. You review a cluster by comparing its real settings with the list, and you fix what the list marks as a risk.

`kube-bench` is an open source tool that runs the benchmark checks on a node and prints a result for each one. The tool only reports. You still decide whether a finding is a real risk, change the setting, and prove that the cluster still works.

## What you will learn

After this module, you can:

- explain how the CIS benchmark is organised and which component each section covers;
- find the manifests, configuration files and certificates of a kubeadm cluster on a node;
- read a `kube-bench` check (its audit, test and remediation) and run the same audit by hand;
- review the effective kubelet configuration and the permissions of its files;
- correct an API server flag in the static pod manifest, wait for the API server to return, and verify the new value.

## How the module is laid out

You start with **The Benchmark And Where The Settings Live**, which maps the sections of the benchmark to the files of a kubeadm node. **Read A Check: kube-bench And The Manual Audit** then shows what a check runs and how to repeat its audit for the API server and etcd. **Review The Kubelet: Effective Configuration And File Permissions** reads the settings the kubelet really uses and fixes a file permission finding. **Correct A Finding Safely And Record It** closes the module: it changes one API server flag without breaking the cluster and records the decision.

A lab follows each part, so you can practise the skill right away.

## Before you start

You should know the Kubernetes basics: pods, namespaces, the control plane and `kubectl`. You should also be able to work in a Linux shell and run commands with `sudo`.

## Your playground

Your playground is one virtual machine (VM) that runs a single-node Kubernetes v1.35 cluster. The cluster was built with kubeadm, the standard tool that installs a cluster on a Linux machine. The node `astro-ats-031-playground-020-01` is the control plane and also runs your pods, so the kubelet checks and the control plane checks run on the same machine.

| Where | Object | What it is |
| --- | --- | --- |
| node `astro-ats-031-playground-020-01` | `kube-bench` binary | The tool that runs the benchmark checks on the node |
| `starfleet` namespace | `probe` Deployment, two pods | A small web server |
| `starfleet` namespace | `probe` Service | Sends requests to the `probe` pods |
| `starfleet` namespace | `shuttle` pod | A client pod |
| `outpost` namespace | `drifter` pod | A client pod in another namespace |

You open a shell on the node with `astrona ssh astro-ats-031-playground-020-01`. You log in as the `student` user. This user can run commands as root with `sudo` and already has `kubectl` set up for the cluster.

Start your playground now and keep it running while you read:

<!-- astrona:playground -->
