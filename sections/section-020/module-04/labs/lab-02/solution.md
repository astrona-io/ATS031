---
exam_objectives:
- Use CIS benchmark to review the security configuration of Kubernetes components
  (etcd, kubelet, kubedns, kubeapi)
---
# Record How The API Server Connects To etcd Solution

Connect to this lab from a host shell. The command `astrona kubeconfig` prints the path of the lab's kubeconfig, the file that tells `kubectl` which cluster to use and which credentials to send. The two variables hold the names of the node containers: `node_name` is the control plane node and `worker_name` is the worker node.

```sh
export KUBECONFIG="$(astrona kubeconfig ats-031-lab-020-04-02)"
test "$(kubectl config current-context)" = "kind-astro-ats-031-lab-020-04-02" || exit 1
node_name="astro-ats-031-lab-020-04-02-control-plane"
worker_name="astro-ats-031-lab-020-04-02-worker"
```

Run node commands as `podman exec "$node_name" ...` or `podman exec "$worker_name" ...`. They change only the node containers of this lab, not your own computer.

## Read the flags of the running API server

The API server is the only Kubernetes component that talks to etcd. Its `--etcd-*` flags say where etcd is and which files it uses for mutual TLS (both sides show a certificate). The static pod manifest shows what the kubelet should start, but the process shows what really runs. Read the command line of the process on the control plane node:

```sh
podman exec "$node_name" sh -c 'tr "\0" "\n" < /proc/$(pgrep -n kube-apiserver)/cmdline' | grep -e '^--etcd'
```

The output has four lines. `--etcd-servers` names the client address of etcd. `--etcd-certfile` and `--etcd-keyfile` are the client certificate and its private key, which prove the identity of the API server to etcd. `--etcd-cafile` is the certificate authority (CA) file that the API server uses to check the certificate of etcd.

## Record the values

Copy each value without the flag name into the ConfigMap. Replace the placeholders with the values you read:

```sh
kubectl -n starfleet-031-020-04-02 create configmap etcd-connection --from-literal=servers=<SERVERS> --from-literal=client-certificate=<CERTFILE> --from-literal=client-key=<KEYFILE> --from-literal=ca-file=<CAFILE>
kubectl -n starfleet-031-020-04-02 get configmap etcd-connection -o yaml
```

The address points to the loopback address `127.0.0.1`, because etcd and the API server run on the same node. The certificate files are in `/etc/kubernetes/pki`, not in `/etc/kubernetes/pki/etcd`, because they belong to the API server, not to etcd.

## Common pitfalls

> [!WARNING]
> The files in `/etc/kubernetes/pki/etcd` are the certificates of etcd itself; the API server uses its own `apiserver-etcd-client` pair. The manifest and the running process can differ after a failed edit, so read the process. Keep the full path in each value.
