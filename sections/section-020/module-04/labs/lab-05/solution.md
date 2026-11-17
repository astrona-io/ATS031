---
exam_objectives:
- Use CIS benchmark to review the security configuration of Kubernetes components
  (etcd, kubelet, kubedns, kubeapi)
---
# Find A Secret Directly In etcd Solution

Connect to this lab from a host shell. The command `astrona kubeconfig` prints the path of the lab's kubeconfig, the file that tells `kubectl` which cluster to use and which credentials to send. The two variables hold the names of the node containers: `node_name` is the control plane node and `worker_name` is the worker node.

```sh
export KUBECONFIG="$(astrona kubeconfig ats-031-lab-020-04-05)"
test "$(kubectl config current-context)" = "kind-astro-ats-031-lab-020-04-05" || exit 1
node_name="astro-ats-031-lab-020-04-05-control-plane"
worker_name="astro-ats-031-lab-020-04-05-worker"
```

Run node commands as `podman exec "$node_name" ...` or `podman exec "$worker_name" ...`. They change only the node containers of this lab, not your own computer.

## Connect to etcd

`etcdctl` is the command-line client of etcd. The etcd image contains it, so the easiest place to run it is the etcd pod itself. etcd accepts only clients with a certificate from its CA, so every call needs three files: the CA file, a client certificate and its key. kubeadm creates the `healthcheck-client` pair for this kind of check. Test the connection:

```sh
kubectl -n kube-system exec "etcd-$node_name" -- etcdctl --endpoints=https://127.0.0.1:2379 --cacert=/etc/kubernetes/pki/etcd/ca.crt --cert=/etc/kubernetes/pki/etcd/healthcheck-client.crt --key=/etc/kubernetes/pki/etcd/healthcheck-client.key endpoint health
```

The output reports the endpoint `https://127.0.0.1:2379` as healthy.

## List the members

An etcd cluster has one or more members. Each member has a name, set with the `--name` flag of etcd:

```sh
kubectl -n kube-system exec "etcd-$node_name" -- etcdctl --endpoints=https://127.0.0.1:2379 --cacert=/etc/kubernetes/pki/etcd/ca.crt --cert=/etc/kubernetes/pki/etcd/healthcheck-client.crt --key=/etc/kubernetes/pki/etcd/healthcheck-client.key member list -w table
```

The table has one row, because this cluster has one control plane node. The `NAME` column holds the member name.

## Find the Secret

The API server stores every object under a key that starts with `/registry/`, followed by the resource type, the namespace and the object name. List only the keys of the Secrets and filter for the name:

```sh
kubectl -n kube-system exec "etcd-$node_name" -- etcdctl --endpoints=https://127.0.0.1:2379 --cacert=/etc/kubernetes/pki/etcd/ca.crt --cert=/etc/kubernetes/pki/etcd/healthcheck-client.crt --key=/etc/kubernetes/pki/etcd/healthcheck-client.key get /registry/secrets/ --prefix --keys-only | grep relay-token
```

The output is one key. The part between `/registry/secrets/` and `/relay-token` is the namespace.

## Record the results

Create the ConfigMap. Replace the placeholders with the key, the namespace and the member name you read:

```sh
kubectl -n starfleet-031-020-04-05 create configmap etcd-query --from-literal=secret-key=<KEY> --from-literal=secret-namespace=<NAMESPACE> --from-literal=member-name=<MEMBER>
kubectl -n starfleet-031-020-04-05 get configmap etcd-query -o yaml
```

The Secret value under this key is readable by anyone who holds an etcd client certificate, because no encryption at rest is configured in this cluster.

## Common pitfalls

> [!WARNING]
> Without `--keys-only`, etcdctl also prints the stored values, which can be long binary data. Without the three certificate options etcdctl cannot connect, because etcd demands a client certificate. The member name is not always the node name; read it from `member list`.
