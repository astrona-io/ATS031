# Restrict Control Plane Kubeconfig And Key Files — Solution

You solve this lab with two `chmod` commands on the control plane node. Keep `astrona submit --watch` running in a second terminal: it grades the lab again and again while you work and records nothing. Each check below turns green as you finish its task.

## Step 1: look at the starting state

The CIS (Center for Internet Security) Kubernetes Benchmark asks for mode `600` or stricter on kubeconfig files and private key files, with the owner `root`. A kubeconfig file holds a client certificate and its private key, so anyone who can read it can act as that client. List the mode, the owner and the path of every kubeconfig file on the control plane node:

```sh
sudo sh -c "stat -c '%a %U:%G %n' /etc/kubernetes/*.conf"
```

The `stat` format prints the mode in octal, then the owner and group, then the path. Look for any line that starts with a mode wider than `600`, such as `644`. Next, use `find` to list the private key files under the `pki` directory, including the `etcd` subdirectory:

```sh
sudo find /etc/kubernetes/pki -name '*.key' -exec stat -c '%a %U:%G %n' {} +
```

The output shows a few `.key` files with mode `644`, in `/etc/kubernetes/pki` and in `/etc/kubernetes/pki/etcd`.

## Step 2: restrict the kubeconfig files (check `kubeconfig-files`)

The `chmod` command changes the mode of a file. A wildcard needs a shell that runs as root, so the command runs through `sh -c`:

```sh
sudo sh -c 'chmod 600 /etc/kubernetes/*.conf'
```

Mode `600` on files that already have `600` changes nothing, so you do not need to pick the wide files one by one.

## Step 3: restrict the key files (checks `key-files` and `etcd-key-files`)

Let `find` call `chmod` on every key file it finds. `find` walks into subdirectories, so one command covers both `/etc/kubernetes/pki` and `/etc/kubernetes/pki/etcd`:

```sh
sudo find /etc/kubernetes/pki -name '*.key' -exec chmod 600 {} +
```

The components read these files when they start, so no restart is needed.

## Step 4: test the result

Run the two `stat` commands from the first step again:

```sh
sudo sh -c "stat -c '%a %U:%G %n' /etc/kubernetes/*.conf"
sudo find /etc/kubernetes/pki -name '*.key' -exec stat -c '%a %U:%G %n' {} +
```

Every line now starts with `600 root:root`. Then check that the API server still answers:

```sh
kubectl get --raw=/readyz
```

The command prints `ok`.

## Step 5: submit

When `astrona submit --watch` shows every check passing, stop it and run `astrona submit`. This grades the lab for real, ends the attempt and removes the lab.

## Common pitfalls

> [!WARNING]
> Every check fails when a certificate file (`*.crt`) under `/etc/kubernetes/pki` no longer has mode `644` and owner `root:root`. Certificates hold no secret, some clients need to read them, and the benchmark checks their mode only as a manual check, so do not restrict them by habit.
>
> A pattern such as `/etc/kubernetes/pki/*.key` misses the files in `/etc/kubernetes/pki/etcd`, and the `etcd-key-files` check stays red.
>
> Keep the owner `root:root`. The grader also rejects a file with the right mode and another owner.
