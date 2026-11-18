---
exam_objectives:
- Use CIS benchmark to review the security configuration of Kubernetes components
  (etcd, kubelet, kubedns, kubeapi)
---
# Disable Profiling And Raise The API Server TLS Minimum Solution

Open a shell on the lab VM (virtual machine) and check that kubectl uses this lab's cluster:

```sh
astrona ssh astro-ats-031-lab-020-03-02
kubectl config current-context
```

The second command prints `kubernetes-admin@astro-ats-031-lab-020-03-02`. You are logged in as the `student` user, which has a kubeconfig file for the cluster. A kubeconfig file tells `kubectl` which cluster to use and which credentials to send. Node files and processes belong to root, so run node commands with `sudo`. They change only the lab VM, not your own computer.

## Confirm both findings

The profiling endpoint `/debug/pprof/` returns data about the memory and CPU use of the API server. Any user who is allowed to read it can learn about the inside of the server, and heavy profiling requests use resources. Request it with your administrator credentials, then read the two flags of the running process:

```sh
kubectl get --raw /debug/pprof/ | head -n 5
sudo ps -eo args | grep '^kube-apiserver' | tr ' ' '\n' | grep -e '--profiling' -e '--tls-min-version'
```

The first command prints the start of an HTML page, so the endpoint answers. The second shows `--tls-min-version=VersionTLS10` and no `--profiling` flag, so profiling has its default value `true`.

## Change both flags

TLS 1.0 and 1.1 have known weaknesses. The benchmark asks for TLS 1.2 or newer. Change the TLS line and add `--profiling=false` in the same edit, so the API server restarts only once. The kubelet watches `/etc/kubernetes/manifests` and starts every file in it as a static pod. Edit a copy in a work directory outside that folder, check the copy, and move it back in one step, so that the kubelet never reads a half-written file:

```sh
sudo mkdir -p /etc/kubernetes/edit
sudo cp -p /etc/kubernetes/manifests/kube-apiserver.yaml /etc/kubernetes/edit/kube-apiserver.yaml
sudo sed -i -e 's|--tls-min-version=VersionTLS10|--tls-min-version=VersionTLS12|' -e 's|^\( *\)- kube-apiserver$|&\n\1- --profiling=false|' /etc/kubernetes/edit/kube-apiserver.yaml
sudo grep -e '--profiling' -e '--tls-min-version' /etc/kubernetes/edit/kube-apiserver.yaml
sudo mv /etc/kubernetes/edit/kube-apiserver.yaml /etc/kubernetes/manifests/kube-apiserver.yaml
```

## Verify the running API server

The kubelet sees the changed file and starts a new API server; on the lab VM that takes about 45 seconds, and kubectl fails until it is back. Wait until the API server answers, then repeat the checks:

```sh
kubectl get --raw=/readyz
sudo ps -eo args | grep '^kube-apiserver' | tr ' ' '\n' | grep -e '--profiling' -e '--tls-min-version'
kubectl get --raw /debug/pprof/
```

The process now has `--profiling=false` and `--tls-min-version=VersionTLS12`, and the last command fails with `the server could not find the requested resource`, which is HTTP `404`.

## Common pitfalls

> [!WARNING]
> A `--profiling=false` line in the manifest does nothing until the new process runs; check the process. A second `--tls-min-version` flag overrides the first, so remove the old line instead of adding one. Valid values are `VersionTLS12` and `VersionTLS13`, not `1.2`.
