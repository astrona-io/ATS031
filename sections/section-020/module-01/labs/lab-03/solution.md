---
exam_objectives:
- Use CIS benchmark to review the security configuration of Kubernetes components
  (etcd, kubelet, kubedns, kubeapi)
---
# Record A Manual Audit Of The API Server And etcd Solution

Open a shell on the lab VM (virtual machine) and check that kubectl uses this lab's cluster:

```sh
astrona ssh astro-ats-031-lab-020-01-03
kubectl config current-context
```

The second command prints `kubernetes-admin@astro-ats-031-lab-020-01-03`. You are logged in as the `student` user, which has a kubeconfig file for the cluster. A kubeconfig file tells `kubectl` which cluster to use and which credentials to send. Node files and processes belong to root, so run node commands with `sudo`. They change only the lab VM, not your own computer.

## Read the running API server

A manual audit reads the value that the component really uses. The kubelet starts each control plane component from a static pod manifest, and the flags in that manifest become the command line of the process. The `ps` command in the node shows that command line. Print it with one flag on each line:

```sh
sudo ps -eo args | grep '^kube-apiserver' | tr ' ' '\n' | grep -e '--authorization-mode' -e '--profiling'
```

The line `--authorization-mode=...` holds the first value to record. Copy it exactly as written. If the output has no `--profiling` line, the flag is not set and the default `true` applies. If it shows `--profiling=false`, record `false`.

## Read etcd and its data directory

The etcd process runs on the same node. Read its client certificate flag the same way:

```sh
sudo ps -eo args | grep '^etcd' | tr ' ' '\n' | grep -e '--client-cert-auth'
```

A kubeadm cluster sets `--client-cert-auth=true`. If the flag were missing, the default `false` would apply. The data directory is a path on the node, so read its mode with `stat`:

```sh
sudo stat -c '%a %U:%G %n' /var/lib/etcd
```

The first field is the octal mode. The benchmark asks for `700` or stricter. A wider mode is a finding, but this task only records it.

## Record the result

Save this as `configmap-manual-audit.yaml`, and replace each placeholder with the value you read. Quote every value, so that a value such as `700` stays a string:

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: manual-audit
  namespace: starfleet-031-020-01-03
data:
  apiserver-authorization-mode: "<AUTHORIZATION_MODE>"
  apiserver-profiling: "<true-or-false>"
  etcd-client-cert-auth: "<true-or-false>"
  etcd-data-dir-mode: "<MODE>"
```

Apply it:

```sh
kubectl apply -f configmap-manual-audit.yaml
```

Then check the result:

```sh
kubectl -n starfleet-031-020-01-03 get configmap manual-audit -o yaml
```

The `data` section shows the four values you read from the node.

## Common pitfalls

> [!WARNING]
> Reading the manifest file can show a value that is not running yet, for example while the kubelet restarts the pod; read the process. A missing flag is not an empty value: it means the default applies, so know the default of each flag. Do not fix a finding in an audit task; the grader compares your record with the current state.
