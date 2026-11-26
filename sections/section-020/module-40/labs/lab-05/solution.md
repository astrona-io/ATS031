# Find A Secret Directly In etcd — Solution

You solve this lab with read-only `etcdctl` commands and one ConfigMap. Keep `astrona submit --watch` running in a second terminal: it grades the lab again and again while you work and records nothing. Each check below turns green as you finish its task.

## Step 1: look at the starting state

`etcdctl` is the command-line client of etcd. The etcd image contains it, so the easiest place to run it is the etcd pod itself, which is named `etcd-` followed by the node name. etcd accepts only clients with a certificate from its certificate authority (CA), so every call needs three files: the CA file, a client certificate and its key. kubeadm creates the `healthcheck-client` pair for this kind of check. Test the connection:

```sh
kubectl -n kube-system exec "etcd-$(hostname)" -- etcdctl --endpoints=https://127.0.0.1:2379 --cacert=/etc/kubernetes/pki/etcd/ca.crt --cert=/etc/kubernetes/pki/etcd/healthcheck-client.crt --key=/etc/kubernetes/pki/etcd/healthcheck-client.key endpoint health
```

The output reports the endpoint `https://127.0.0.1:2379` as healthy.

## Step 2: find the etcd key of the Secret (check `secret-key-recorded`)

The API server stores every object under a key that starts with `/registry/`, followed by the resource type, the namespace and the object name. List only the keys of the Secrets and filter for the name:

```sh
kubectl -n kube-system exec "etcd-$(hostname)" -- etcdctl --endpoints=https://127.0.0.1:2379 --cacert=/etc/kubernetes/pki/etcd/ca.crt --cert=/etc/kubernetes/pki/etcd/healthcheck-client.crt --key=/etc/kubernetes/pki/etcd/healthcheck-client.key get /registry/secrets/ --prefix --keys-only | grep '/relay-token$'
```

The output is one key. Note it as `<KEY>`.

## Step 3: read the namespace from the key (check `secret-located`)

The part between `/registry/secrets/` and `/relay-token` is the namespace. Note it as `<NAMESPACE>`.

## Step 4: read the member name (check `member-recorded`)

An etcd cluster has one or more members. Each member has a name, set with the `--name` flag of etcd:

```sh
kubectl -n kube-system exec "etcd-$(hostname)" -- etcdctl --endpoints=https://127.0.0.1:2379 --cacert=/etc/kubernetes/pki/etcd/ca.crt --cert=/etc/kubernetes/pki/etcd/healthcheck-client.crt --key=/etc/kubernetes/pki/etcd/healthcheck-client.key member list -w table
```

The table has one row, because this cluster has one control plane node. Note the value in the `NAME` column as `<MEMBER>`.

## Step 5: save the ConfigMap

Create the ConfigMap with the three values. Replace each placeholder with the value you noted:

```sh
kubectl -n starfleet-031-020-04-05 create configmap etcd-query --from-literal=secret-key=<KEY> --from-literal=secret-namespace=<NAMESPACE> --from-literal=member-name=<MEMBER>
```

All three checks turn green at once. The Secret value under this key is readable by anyone who holds an etcd client certificate, because no encryption at rest is configured in this cluster.

## Step 6: test the result

Print the saved values and compare them with the name of the running etcd member:

```sh
kubectl -n starfleet-031-020-04-05 get configmap etcd-query -o jsonpath='{.data}'; echo
sudo sh -c 'tr "\0" "\n" < /proc/$(pgrep -n etcd)/cmdline' | grep -e '^--name'
```

The `secret-key` value starts with `/registry/secrets/` and ends with `/relay-token`, `secret-namespace` is the part in between, and `member-name` is the same as the text after `--name=`.

## Step 7: submit

When `astrona submit --watch` shows every check passing, stop it and run `astrona submit`. This grades the lab for real, ends the attempt and removes the lab.

## Common pitfalls

> [!WARNING]
> Save the full key, starting with `/registry/secrets/`. A key without the prefix or with a trailing `/` fails.
>
> Without `--keys-only`, etcdctl also prints the stored values, which can be long binary data. Without the three certificate options etcdctl cannot connect, because etcd demands a client certificate.
>
> Read the member name from `member list`. The grader compares it with the `--name` flag of the running etcd process.
