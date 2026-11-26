# Disable Profiling And Raise The API Server TLS Minimum — Solution

You solve this lab with one edit of the API server static pod manifest. Keep `astrona submit --watch` running in a second terminal: it grades the lab again and again while you work and records nothing. Each check below turns green as you finish its task.

## Step 1: look at the starting state

The profiling endpoint `/debug/pprof/` returns data about the memory and CPU use of the API server. Any user who is allowed to read it can learn about the inside of the server, and heavy profiling requests use resources. Request it with your administrator credentials, then read the two flags of the running process:

```sh
kubectl get --raw /debug/pprof/ | head -n 5
sudo ps -eo args | grep '^kube-apiserver' | tr ' ' '\n' | grep -e '--profiling' -e '--tls-min-version'
```

The first command prints the start of an HTML page, so the endpoint answers. The second shows `--tls-min-version=VersionTLS10` and no `--profiling` flag, so profiling has its default value `true`.

## Step 2: copy the manifest

The kubelet watches `/etc/kubernetes/manifests` and starts every file in it as a static pod, a pod that the kubelet runs from a file on the node. Edit a copy in a work directory outside that folder, so that the kubelet never reads a half-written file and no backup becomes a second pod:

```sh
sudo mkdir -p /etc/kubernetes/edit
sudo cp -p /etc/kubernetes/manifests/kube-apiserver.yaml /etc/kubernetes/edit/kube-apiserver.yaml
```

Both flag changes go into this copy, so the API server restarts only once.

## Step 3: turn off profiling (check `api-profiling-disabled`)

Add `--profiling=false` right after the line `- kube-apiserver`, with the same indentation as the other flags:

```sh
sudo sed -i 's|^\( *\)- kube-apiserver$|&\n\1- --profiling=false|' /etc/kubernetes/edit/kube-apiserver.yaml
```

## Step 4: raise the TLS minimum (check `tls-min-version`)

TLS 1.0 and 1.1 have known weaknesses. The benchmark asks for TLS 1.2 or newer. Change the existing line instead of adding a second one:

```sh
sudo sed -i 's|--tls-min-version=VersionTLS10|--tls-min-version=VersionTLS12|' /etc/kubernetes/edit/kube-apiserver.yaml
sudo grep -e '--profiling' -e '--tls-min-version' /etc/kubernetes/edit/kube-apiserver.yaml
```

The `grep` prints `- --profiling=false` and `- --tls-min-version=VersionTLS12`. Move the copy back in one step:

```sh
sudo mv /etc/kubernetes/edit/kube-apiserver.yaml /etc/kubernetes/manifests/kube-apiserver.yaml
```

## Step 5: wait for the new API server (check `pprof-not-found`)

The kubelet sees the changed file and starts a new API server; kubectl fails until it is back. Wait until it answers:

```sh
for attempt in $(seq 1 60); do
  if sudo ps -eo args | grep '^kube-apiserver ' | grep -q -e '--profiling=false' && kubectl --request-timeout=3s get --raw=/readyz >/dev/null 2>&1; then echo "new flag visible and API server ready"; break; fi
  sleep 3
done
```

The old API server process can still answer for a few seconds after the `mv`, so the loop waits until the running process has the new flag and the API server is ready. It prints `new flag visible and API server ready`. If it ends without that message, run `sudo crictl ps -a --name kube-apiserver` and read the logs of the exited container with `sudo crictl logs <CONTAINER_ID>`.

## Step 6: test the result

```sh
sudo ps -eo args | grep '^kube-apiserver' | tr ' ' '\n' | grep -e '--profiling' -e '--tls-min-version'
kubectl get --raw /debug/pprof/
```

The process now has `--profiling=false` and `--tls-min-version=VersionTLS12`. The last command fails with a `NotFound` error, which is HTTP `404`.

## Step 7: submit

When `astrona submit --watch` shows every check passing, stop it and run `astrona submit`. This grades the lab for real, ends the attempt and removes the lab.

## Common pitfalls

> [!WARNING]
> The grader reads the running `kube-apiserver` process, not the manifest. A flag in the file does nothing until the new process runs.
>
> A second `--tls-min-version` flag overrides the first: the last one wins. Valid values are `VersionTLS12` and `VersionTLS13`, not `1.2`.
