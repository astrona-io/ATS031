# Record A Manual Audit Of The API Server And etcd — Solution

You solve this lab by reading two processes and one directory on the control plane node, then writing one ConfigMap. Keep `astrona submit --watch` running in a second terminal: it grades the lab again and again while you work and records nothing. Each check below turns green as you finish its task.

## Step 1: look at the starting state

A manual audit reads the value that the component really uses. The kubelet starts each control plane component from a static pod manifest in `/etc/kubernetes/manifests`, and the flags in that manifest become the command line of the process. The `ps` command shows that command line. Check that the ConfigMap does not exist yet:

```sh
kubectl -n starfleet-031-020-01-03 get configmap manual-audit
```

The command fails with `NotFound`.

## Step 2: read the API server values (check `apiserver-values`)

Print the command line of the running API server with one flag on each line:

```sh
sudo ps -eo args | grep '^kube-apiserver' | tr ' ' '\n' | grep -e '--authorization-mode' -e '--profiling'
```

The output has the line `--authorization-mode=Node,RBAC`. Copy the value exactly as written. The `--profiling` flag depends on the start of the lab. If the output has no `--profiling` line, the flag is not set and the default `true` applies. If it shows `--profiling=false`, record `false`.

## Step 3: read the etcd client certificate setting (check `etcd-values`)

The etcd process runs on the same node. Read its client certificate flag the same way:

```sh
sudo ps -eo args | grep '^etcd' | tr ' ' '\n' | grep -e '--client-cert-auth'
```

The output is `--client-cert-auth=true`: kubeadm sets this flag. If the flag were missing, the default `false` would apply.

## Step 4: read the etcd data directory mode (check `etcd-data-dir-mode`)

The data directory is a path on the node, so read its mode with `stat`:

```sh
sudo stat -c '%a %U:%G %n' /var/lib/etcd
```

The first field is the octal mode, for example `700`, `750` or `755`. The benchmark asks for `700` or stricter. A wider mode is a finding, but this task only records it.

## Step 5: record the values

Save this as `configmap-manual-audit.yaml`. Replace `<PROFILING>` with the profiling value from step 2 and `<MODE>` with the mode from step 4. Quote every value, so that a value such as `700` stays a string:

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: manual-audit
  namespace: starfleet-031-020-01-03
data:
  apiserver-authorization-mode: "Node,RBAC"
  apiserver-profiling: "<PROFILING>"
  etcd-client-cert-auth: "true"
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

## Step 6: submit

When `astrona submit --watch` shows every check passing, stop it and run `astrona submit`. This grades the lab for real, ends the attempt and removes the lab.

## Common pitfalls

> [!WARNING]
> Do not fix a finding in an audit task. Every check fails when the API server `--profiling` or `--authorization-mode`, the etcd `--client-cert-auth` or the mode of `/var/lib/etcd` differs from the start of the lab.
>
> A missing flag is not an empty value: it means the default applies. Record `true` for a missing `--profiling` and `false` for a missing `--client-cert-auth`.
>
> Copy values as the node prints them. `Node,RBAC` with a space, or a mode such as `0700` instead of `700`, does not match.
