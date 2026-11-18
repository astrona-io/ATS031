---
exam_objectives:
- Use CIS benchmark to review the security configuration of Kubernetes components
  (etcd, kubelet, kubedns, kubeapi)
---
# Query etcd With etcdctl

Flags and file modes tell you how etcd is configured. A direct query tells you what an attacker would get. `etcdctl` is the command-line client for etcd. In this part you connect with a valid client certificate, list keys, read a Secret and see that the value is plain text. The result explains why the next part encrypts Secrets even when TLS and file permissions are correct.

## Where to run etcdctl

The playground node has no `etcdctl` binary, but the etcd container image includes one, and the etcd pod already mounts the certificates in `/etc/kubernetes/pki/etcd`. The simplest way to run the client is `kubectl exec` into the etcd pod. The etcd image is small and may have no shell, so the commands below call `etcdctl` directly, not through `sh -c`. On a node that has its own `etcdctl` binary, you can run it with `sudo` and the same flags.

`etcdctl` version 3.4 and later uses the version 3 API by default. Older clients need the environment variable `ETCDCTL_API=3`. The client needs four values for every command: the endpoint, the CA, the client certificate and the client key. The health-check client certificate that kubeadm creates for etcd is enough for the queries here.

## Check health and members

Open a shell on the node, set the node name and the pod name, then ask etcd for its health and list its members:

<!-- astrona:playground:renew -->

```sh
astrona ssh astro-ats-031-playground-020-04
NODE=astro-ats-031-playground-020-04
ETCD_POD=etcd-$NODE
kubectl -n kube-system exec $ETCD_POD -- etcdctl --endpoints=https://127.0.0.1:2379 --cacert=/etc/kubernetes/pki/etcd/ca.crt --cert=/etc/kubernetes/pki/etcd/healthcheck-client.crt --key=/etc/kubernetes/pki/etcd/healthcheck-client.key endpoint health
kubectl -n kube-system exec $ETCD_POD -- etcdctl --endpoints=https://127.0.0.1:2379 --cacert=/etc/kubernetes/pki/etcd/ca.crt --cert=/etc/kubernetes/pki/etcd/healthcheck-client.crt --key=/etc/kubernetes/pki/etcd/healthcheck-client.key member list
```

The output on the playground node (the time, the member ID and the addresses differ on your node):

```text
https://127.0.0.1:2379 is healthy: successfully committed proposal: took = 5.491683ms
f074a195de705325, started, astro-ats-031-playground-020-04, https://10.0.2.15:2380, https://10.0.2.15:2379, false
```

The endpoint is healthy. The command ran inside the pod, so it reached etcd on the loopback address. The member list has one member, which is the control plane node. The member advertises the peer port `2380` and the client port `2379` on the node address. The last field, `false`, says the member is not a learner, which is a member that only receives data and does not vote yet.

## List the keys

Keys are strings. The option `--prefix` selects every key that starts with the given text, and `--keys-only` hides the values. This command lists the keys for Secrets:

```sh
kubectl -n kube-system exec $ETCD_POD -- etcdctl --endpoints=https://127.0.0.1:2379 --cacert=/etc/kubernetes/pki/etcd/ca.crt --cert=/etc/kubernetes/pki/etcd/healthcheck-client.crt --key=/etc/kubernetes/pki/etcd/healthcheck-client.key get /registry/secrets --prefix --keys-only
```

The output on the playground node (the name of the bootstrap token differs on your node; `etcdctl` prints an empty line after each key):

```text
/registry/secrets/kube-system/bootstrap-token-rrlue1

/registry/secrets/starfleet/launch-code

```

The result lists a key for each Secret in each namespace: the Secret `launch-code` and the bootstrap token that kubeadm created for joining nodes. Kubernetes v1.24 and later no longer create a Secret for each service account token, so a new cluster has few Secrets. The key shows the namespace and the name of every Secret without any read permission in Kubernetes. Kubernetes RBAC is not involved, because this request does not go through the API server.

## Read a value

The next command reads the Secret `launch-code`. The value is binary, so the command prints only the value and the `grep` looks for a readable word inside it. The option `-a` of `grep` tells it to treat binary data as text, and `-o` prints only the matching text:

```sh
kubectl -n kube-system exec $ETCD_POD -- etcdctl --endpoints=https://127.0.0.1:2379 --cacert=/etc/kubernetes/pki/etcd/ca.crt --cert=/etc/kubernetes/pki/etcd/healthcheck-client.crt --key=/etc/kubernetes/pki/etcd/healthcheck-client.key get /registry/secrets/starfleet/launch-code --print-value-only | grep -a -o 'warp-nine-launch'
```

The output is:

```text
warp-nine-launch
warp-nine-launch
```

This is the code stored in the Secret. It appears twice because the playground created the Secret with `kubectl apply`, which also stores a copy of the applied object in the annotation `kubectl.kubernetes.io/last-applied-configuration`. The Kubernetes API shows the value base64 encoded, and base64 is an encoding, not encryption. In etcd the value is not even encoded. Anyone with a valid etcd client certificate, or with a copy of the data files, reads it in clear text.

To compare, read the same Secret through the API server, where RBAC applies:

```sh
kubectl -n starfleet get secret launch-code -o jsonpath='{.data.code}' | base64 -d; echo
```

The output is the same code. The API path requires authentication and authorization. The etcd path requires only a certificate from the etcd CA, which is why the benchmark protects the certificates, the data directory and the network access so strictly.

## What this shows

The query proved three things. etcd answers a client with a valid certificate, which is the intended behavior. The names of all Secrets are readable at the key level. The values are plain text. TLS and `--client-cert-auth` protect the connection, and file permissions protect the disk, but neither protects the data itself if a certificate, a backup or a disk copy leaks.

Encryption at rest covers this last gap. It makes the API server encrypt the value before it writes it to etcd, so that a stolen copy contains ciphertext. The next part configures it.

## Common pitfalls

> [!WARNING]
> - **Running etcdctl against the cluster you do not own.** Only query your own training cluster. A client certificate from etcd grants read and write access to everything.
> - **Printing Secret values into shared logs or terminals.** Use a filter that prints only the word you look for, as above.
> - **Forgetting the certificate flags.** Without `--cacert`, `--cert` and `--key`, the request fails with a TLS error and says nothing about the data.
> - **Using `etcdctl put` or `del` for tests.** A write bypasses admission and validation and can corrupt the cluster state. Use read commands only.
