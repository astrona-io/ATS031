---
exam_objectives:
- Use CIS benchmark to review the security configuration of Kubernetes components
  (etcd, kubelet, kubedns, kubeapi)
---
# Disable Profiling And Raise The API Server TLS Minimum

Allow about 10 minutes for the tasks.

A penetration test of the `starfleet` API server reports two findings: the profiling endpoint answers, and the server accepts TLS 1.0. Close both.

## Starting state

The lab VM runs a one-node Kubernetes cluster built with kubeadm, the standard tool that installs a cluster on a Linux machine. The node `astro-ats-031-lab-020-03-02` is the control plane and also runs the pods. The `starfleet-031-020-03-02` namespace runs two `probe` replicas behind the `probe` Service and a `shuttle` client pod. The API server runs with the profiling endpoint on (the default) and with `--tls-min-version=VersionTLS10`.

Open a shell on the lab VM (virtual machine) and check that kubectl uses this lab's cluster:

```sh
astrona ssh astro-ats-031-lab-020-03-02
kubectl config current-context
```

The second command prints `kubernetes-admin@astro-ats-031-lab-020-03-02`. You are logged in as the `student` user, which has a kubeconfig file for the cluster. A kubeconfig file tells `kubectl` which cluster to use and which credentials to send. Node files and processes belong to root, so run node commands with `sudo`. They change only the lab VM, not your own computer.

## Required result

- The API server runs with `--profiling=false`, and a request to `/debug/pprof/` returns HTTP `404`.
- The API server runs with `--tls-min-version=VersionTLS12` or `--tls-min-version=VersionTLS13`.
- The API server stays ready and both `probe` replicas stay available.

## Verify The Result

The grader reads the command line of the running `kube-apiserver` process and requests `/debug/pprof/` with administrator credentials.
