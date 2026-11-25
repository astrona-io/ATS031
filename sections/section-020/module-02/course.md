# Run kube-bench And Read Its Output

The Center for Internet Security (CIS) Kubernetes Benchmark is a long list of recommended security settings for a cluster. Nobody checks hundreds of settings by hand, not in a security review and not in an exam. You need a tool that does the checking for you.

`kube-bench` is that tool. It is an open source program that runs the audit commands of the benchmark on a node and prints one result for each recommendation. An audit command is a short shell command that reads one setting on the node.

A tool report is not a final verdict, though. `kube-bench` reads the processes and files of one node at one moment. It also follows a benchmark edition, a version of the rules, that may not match the Kubernetes version of your cluster. So you need to know what the tool looks at, to tell a real finding from a false one.

## What you will learn

After this module, you can:

- explain what `kube-bench` reads on a node and how it decides `PASS` or `FAIL`;
- run `kube-bench` on a kubeadm node with `sudo`, and as a Kubernetes Job that uses the `kube-bench` container image;
- choose a target and a benchmark edition, and say what happens when the edition does not match the cluster version;
- read the result lines, the summary counts and the remediation text of a failing check;
- run one check or one group, export the result as JSON, and filter it with `jq`;
- explain why `WARN` and `INFO` results need a person, and why a `PASS` is only as good as its audit.

## How the module is laid out

You start with **What kube-bench Does Under The Hood**, which shows what the tool reads and where each result comes from. **Run kube-bench On A kubeadm Node** then runs the tool as a binary on the node and as a Job in the cluster. **Targets, Benchmarks And Versions** explains how to pick the group of checks and the edition of the rules.

**Read A Result** shows the layout of the report and the order in which to read it. **Select Checks And Export Results** reruns single checks and saves results as JSON for a before and after comparison. **Manual Checks And False Findings** closes the module with the results that a person must judge.

## Before you start

You should know the Kubernetes basics: pods, Jobs, namespaces and `kubectl`. You should also be able to open a shell on a Linux machine and run commands with `sudo`.

## Your playground

Your playground is one virtual machine (VM) that runs a single-node Kubernetes v1.35 cluster. The cluster was built with kubeadm, the standard tool that installs Kubernetes on a Linux machine. The node `astro-ats-031-playground-020-02` is the control plane and also runs your pods, so the control plane checks and the kubelet checks run on the same machine.

| Where | Object | What it is |
| --- | --- | --- |
| Node | `astro-ats-031-playground-020-02` | The only node: control plane and workloads |
| Node | `/usr/local/bin/kube-bench` | The `kube-bench` program |
| Node | `/etc/kube-bench/cfg` | The definition files of the benchmark editions |
| Node | `kube-bench` container image | Already on the node, so a pod that uses it starts without a download |
| Node | `jq` | A command-line tool that reads JSON |
| `starfleet` | `probe` Deployment (two pods) and `probe` Service | A small example workload |
| `starfleet` | `shuttle` pod | A client pod |
| `outpost` | `drifter` pod | A client pod in another namespace |

You open a shell on the node with `astrona ssh astro-ats-031-playground-020-02`. You log in as the `student` user. This user can run commands as root with `sudo` and already has `kubectl` set up for the cluster.

Start your playground now and keep it running while you read:

<!-- astrona:playground -->
