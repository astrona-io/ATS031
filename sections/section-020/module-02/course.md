---
exam_objectives:
- Use CIS benchmark to review the security configuration of Kubernetes components
  (etcd, kubelet, kubedns, kubeapi)
---
# Run kube-bench And Read Its Output

The Center for Internet Security (CIS) Kubernetes Benchmark is a long list of recommended settings. Nobody checks hundreds of settings by hand during a review or an exam. `kube-bench` is an open source program that runs the audit commands of the benchmark on a node and prints one result for each recommendation. This module teaches you to run it, to read what it prints, to run only the checks you need, and to judge how far a result can be trusted.

A tool report is not a verdict. `kube-bench` reads the processes and files of one node at one moment, and it follows a benchmark edition that may not match the Kubernetes version of your cluster. You need to know what the tool looks at so that you can tell a real finding from a false one.

## Learning objectives

After this module you can:

- Explain what `kube-bench` reads on a node and how it decides `PASS` or `FAIL`.
- Run `kube-bench` on a kubeadm node with `sudo`, and as a Kubernetes Job that uses the `kube-bench` image.
- Choose a target and a benchmark edition, and say what happens when the edition does not match the cluster version.
- Read the result lines, the summary counts and the remediation text of a failing check.
- Run one check or one group, export the result as JSON, and filter it with `jq`.
- Explain why `WARN` and `INFO` results need a person, and why a `PASS` is only as good as its audit.

## Before you start

You need Kubernetes basics: pods, Jobs, namespaces and `kubectl`. The module has six parts. The first explains what the tool reads. The second runs it on a kubeadm node. The third covers targets, editions and versions. The fourth reads a result. The fifth selects checks and exports results. The sixth covers manual checks and false findings.

Your playground is one virtual machine (VM) that runs a single-node Kubernetes v1.35 cluster built with kubeadm, the standard tool that installs a cluster on a Linux machine. The node `astro-ats-031-playground-020-02` is the control plane and also runs your pods, so the control plane checks and the kubelet checks run on the same machine. The `starfleet` namespace holds the `probe` Deployment (two pods), the `probe` Service and the `shuttle` client pod.

You open a shell on the node with `astrona ssh astro-ats-031-playground-020-02`. You log in as the `student` user, which can run commands as root with `sudo` and already has `kubectl` set up for the cluster. The `kube-bench` binary is installed in `/usr/local/bin/kube-bench`, and its definition files are in `/etc/kube-bench/cfg`. The `kube-bench` container image is already on the node, so a pod that uses it starts without a download. `jq`, a command-line tool that reads JSON, is installed on the node too.

Launch your playground now and keep it running while you read:

<!-- astrona:playground -->
