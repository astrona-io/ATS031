---
exam_objectives:
- Use CIS benchmark to review the security configuration of Kubernetes components
  (etcd, kubelet, kubedns, kubeapi)
---
# Guided Practice: Run kube-bench In A Private Playground

This ungraded playground is one virtual machine (VM) that runs a single-node Kubernetes cluster built with kubeadm, the standard tool that installs a cluster on a Linux machine. The node is the control plane and also runs your pods. kube-bench is the tool that checks a node against the Center for Internet Security (CIS) Kubernetes Benchmark, a published list of secure settings. Its binary is in `/usr/local/bin/kube-bench`, and its benchmark files are in `/etc/kube-bench/cfg`.

Because the node is a real machine, kube-bench reads the real files and processes of the API server, etcd and the kubelet. That is the same work you do on a node in the exam.

<!-- astrona:playground:renew -->

Open a shell on the node. You log in as the `student` user, which has `sudo` and a kubeconfig file for the cluster. A kubeconfig file tells kubectl, the Kubernetes command-line tool, which cluster to use and which credentials to send.

```sh
astrona ssh astro-ats-031-playground-020-02
kubectl config current-context
```

The second command prints `kubernetes-admin@astro-ats-031-playground-020-02`. Commands that use `sudo` change only this VM. They do not touch your own computer.

## Starting state

The `starfleet` namespace has the `probe` Deployment, the `probe` Service and the `shuttle` pod. The cluster uses the kubeadm defaults, so some benchmark checks fail.

```sh
kubectl get nodes -o wide
kubectl -n starfleet get pods
```

The node `astro-ats-031-playground-020-02` is `Ready` and runs Kubernetes `v1.35.10` with containerd `2.2.1`. The two `probe` pods and the `shuttle` pod are `Running`.

## A first run

kube-bench reads files that only root can read, such as the static pod manifests in `/etc/kubernetes/manifests`, so run it with `sudo`. The `master` target checks the control plane components.

```sh
sudo kube-bench run --targets master | tail -5
```

The summary at the end shows the totals. This output is shortened to the last lines:

```text
== Summary total ==
39 checks PASS
9 checks FAIL
11 checks WARN
0 checks INFO
```

kube-bench picks the benchmark edition from the Kubernetes version of the node. On this node it maps version `1.35` to `cis-1.10`. Each line in the full report starts with `[PASS]`, `[FAIL]`, `[WARN]` or `[INFO]` and the check number, so you can always find a check in the benchmark text again.

## Suggested exercises

These exercises use only the node and the commands above.

1. Run the `node` target, which checks the kubelet, and the `etcd` target. Compare their totals with the `master` totals. On this node the `node` target gives 16 PASS, 2 FAIL and 6 WARN, and the `etcd` target gives 7 PASS.
2. Export the `master` result as JSON with `--json` and list the numbers of the failing checks with `jq`, a command-line JSON tool that is installed on the node. On this node the list is `1.1.12 1.2.5 1.2.15 1.2.16 1.2.17 1.2.18 1.2.19 1.3.2 1.4.1`.
3. Run one check with `sudo kube-bench run --check 1.2.15`. Read the remediation text. It tells you to set `--profiling=false` in `/etc/kubernetes/manifests/kube-apiserver.yaml`.
4. Add `--profiling=false` to the API server manifest with `sudo`. The kubelet sees the changed file and restarts the API server static pod; on this node that took about 45 seconds. Run check `1.2.15` again and see that it now shows `[PASS]`.
5. Run `sudo kube-bench run --targets master --v 1` and find the log line that names the benchmark version.

The result of a run in this playground is practice for the workflow. It is not a claim of compliance for any other cluster.

## Common pitfalls

> [!WARNING]
> Run kube-bench with `sudo`: without root it cannot read the manifests and the data directories, and checks fail for the wrong reason. Name the benchmark edition in every note you keep. A broken edit to a static pod manifest stops the API server, so kubectl fails until you fix the file; keep a copy of the file before you edit it.
