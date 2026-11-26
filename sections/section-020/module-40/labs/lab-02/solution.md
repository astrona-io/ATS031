# Record How The API Server Connects To etcd — Solution

You solve this lab by reading four flags of the running API server and saving them in one ConfigMap. Keep `astrona submit --watch` running in a second terminal: it grades the lab again and again while you work and records nothing. Each check below turns green as you finish its task.

## Step 1: look at the starting state

The API server is the only Kubernetes component that talks to etcd. Its `--etcd-*` flags say where etcd is and which files it uses for mutual TLS (both sides show a certificate). The static pod manifest shows what the kubelet should start, but the process shows what really runs. Read the command line of the process on the control plane node:

```sh
sudo sh -c 'tr "\0" "\n" < /proc/$(pgrep -n kube-apiserver)/cmdline' | grep -e '^--etcd'
kubectl -n starfleet-031-020-04-02 get configmap
```

The first command prints four lines, one for each `--etcd-*` flag. The ConfigMap `etcd-connection` does not exist yet, so the second command lists only `kube-root-ca.crt`.

## Step 2: record the etcd address (check `server-recorded`)

`--etcd-servers` names the client address of etcd. It points to the loopback address `127.0.0.1`, because etcd and the API server run on the same node. Note the value after the `=` sign; you save it in Step 5 as `<SERVERS>`.

## Step 3: record the client certificate and key (check `credentials-recorded`)

`--etcd-certfile` and `--etcd-keyfile` are the client certificate and its private key. They prove the identity of the API server to etcd. Note both paths as `<CERTFILE>` and `<KEYFILE>`. They are in `/etc/kubernetes/pki`, not in `/etc/kubernetes/pki/etcd`, because they belong to the API server, not to etcd.

## Step 4: record the CA file (check `ca-recorded`)

`--etcd-cafile` is the certificate authority (CA) file that the API server uses to check the certificate of etcd. Note the path as `<CAFILE>`.

## Step 5: save the ConfigMap

Create the ConfigMap with all four keys. Replace each placeholder with the full value you read, without the flag name:

```sh
kubectl -n starfleet-031-020-04-02 create configmap etcd-connection --from-literal=servers=<SERVERS> --from-literal=client-certificate=<CERTFILE> --from-literal=client-key=<KEYFILE> --from-literal=ca-file=<CAFILE>
```

All three checks turn green at once, because the grader compares each key with the flag it names.

## Step 6: test the result

Print the saved values next to the flags of the running process:

```sh
kubectl -n starfleet-031-020-04-02 get configmap etcd-connection -o jsonpath='{.data}'; echo
sudo sh -c 'tr "\0" "\n" < /proc/$(pgrep -n kube-apiserver)/cmdline' | grep -e '^--etcd'
```

Each value in the first line must be the same as the text after `=` in one of the four flag lines.

## Step 7: submit

When `astrona submit --watch` shows every check passing, stop it and run `astrona submit`. This grades the lab for real, ends the attempt and removes the lab.

## Common pitfalls

> [!WARNING]
> The files in `/etc/kubernetes/pki/etcd` are the certificates of etcd itself; the API server uses its own `apiserver-etcd-client` pair. Copy the values from the process, not from memory.
>
> Keep the full path in each value, without the flag name and the `=` sign. The grader compares the text exactly.
>
> Do not edit a control plane manifest or the kubelet configuration. The grader compares their checksums with the starting state and fails every check after any change.
