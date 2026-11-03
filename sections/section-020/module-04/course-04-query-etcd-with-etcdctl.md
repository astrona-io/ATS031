---
draft: true
exam_objectives:
- Use CIS benchmark to review the security configuration of Kubernetes components
  (etcd, kubelet, kubedns, kubeapi)
---
# Query etcd With etcdctl

Flags and file modes tell you how etcd is configured. A direct query tells you what an attacker would get. `etcdctl` is the command-line client for etcd. In this part you connect with a valid client certificate, list keys, read a Secret and see that the value is plain text. The result explains why the next part encrypts Secrets even when TLS and file permissions are correct.

## Where to run etcdctl

The etcd container image includes `etcdctl`, and the etcd pod already mounts the certificates in `/etc/kubernetes/pki/etcd`. The simplest way to run the client is `kubectl exec` into the etcd pod. The etcd image is small and may have no shell, so the commands below call `etcdctl` directly, not through `sh -c`. If `kubectl exec` reports that it cannot find `etcdctl` in your cluster, the image of your version does not ship the client, and you would run a separate `etcdctl` binary on the node with the same flags.

`etcdctl` version 3.4 and later uses the version 3 API by default. Older clients need the environment variable `ETCDCTL_API=3`. The client needs four values for every command: the endpoint, the CA, the client certificate and the client key. The health-check client certificate that kubeadm creates for etcd is enough for the queries here.

## Check health and members

Set the node name and the pod name, then ask etcd for its health:

<!-- astrona:playground:renew -->

```sh
NODE=astro-ats-031-playground-020-04-control-plane
ETCD_POD=etcd-$NODE
kubectl -n kube-system exec $ETCD_POD -- etcdctl --endpoints=https://127.0.0.1:2379 --cacert=/etc/kubernetes/pki/etcd/ca.crt --cert=/etc/kubernetes/pki/etcd/healthcheck-client.crt --key=/etc/kubernetes/pki/etcd/healthcheck-client.key endpoint health
```

The output says the endpoint is healthy and shows how long the request took. The command ran inside the pod, so it reached etcd on the loopback address. If you list the members with `member list`, you see one member, which is the control plane node.

## List the keys

Keys are strings. The option `--prefix` selects every key that starts with the given text, and `--keys-only` hides the values. This command lists the keys for Secrets:

```sh
kubectl -n kube-system exec $ETCD_POD -- etcdctl --endpoints=https://127.0.0.1:2379 --cacert=/etc/kubernetes/pki/etcd/ca.crt --cert=/etc/kubernetes/pki/etcd/healthcheck-client.crt --key=/etc/kubernetes/pki/etcd/healthcheck-client.key get /registry/secrets --prefix --keys-only
```

The result lists a key for each Secret in each namespace, including `/registry/secrets/starfleet/launch-code`. The list also includes service account token Secrets and bootstrap tokens. The key shows the namespace and the name of every Secret without any read permission in Kubernetes. Kubernetes RBAC is not involved, because this request does not go through the API server.

## Read a value

The next command reads the Secret `launch-code`. The value is binary, so the command prints only the value and the host filter looks for a readable word inside it. The option `-a` of `grep` tells it to treat binary data as text, and `-o` prints only the matching text:

```sh
kubectl -n kube-system exec $ETCD_POD -- etcdctl --endpoints=https://127.0.0.1:2379 --cacert=/etc/kubernetes/pki/etcd/ca.crt --cert=/etc/kubernetes/pki/etcd/healthcheck-client.crt --key=/etc/kubernetes/pki/etcd/healthcheck-client.key get /registry/secrets/starfleet/launch-code --print-value-only | grep -a -o 'warp-nine-launch'
```

The command prints `warp-nine-launch`. This is the code stored in the Secret. The Kubernetes API shows the same value base64 encoded, and base64 is an encoding, not encryption. In etcd the value is not even encoded. Anyone with a valid etcd client certificate, or with a copy of the data files, reads it in clear text.

To compare, read the same Secret through the API server, where RBAC applies:

```sh
kubectl -n starfleet get secret launch-code -o jsonpath='{.data.code}' | base64 -d
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
