---
draft: true
exam_objectives:
- Use CIS benchmark to review the security configuration of Kubernetes components
  (etcd, kubelet, kubedns, kubeapi)
---
# Guided Practice: Inspect etcd And Its Protection

This playground is a private kind cluster with one control plane node and one worker node. etcd runs as a static pod on the control plane node. The Secret `launch-code` in the `starfleet` namespace exists and no encryption configuration is set. The permissions of the etcd data directory are wider than the benchmark allows.

Use a host shell with the private kubeconfig. A kubeconfig identifies the cluster and credentials used by kubectl, the Kubernetes command-line tool.

<!-- astrona:playground:renew -->

```sh
export KUBECONFIG="$(astrona kubeconfig ats-031-playground-020-04)"
test "$(kubectl config current-context)" = "kind-astro-ats-031-playground-020-04" || exit 1
node_name="astro-ats-031-playground-020-04-control-plane"
```

Keep this connection selected. Host-level commands name only this environment's node containers. They do not operate on the host operating system.

## Inspect

Read the TLS flags in the etcd manifest and the mode of the data directory:

```sh
podman exec "$node_name" grep -e 'client-cert-auth' -e 'auto-tls' -e 'data-dir' /etc/kubernetes/manifests/etcd.yaml
podman exec "$node_name" stat -c '%a %U:%G %n' /var/lib/etcd
```

Then read the key of the Secret through the etcd pod. The value is binary, so the filter prints only a readable word. The environment gives no expected output; read what your cluster returns.

```sh
kubectl -n kube-system exec "etcd-$node_name" -- etcdctl --endpoints=https://127.0.0.1:2379 --cacert=/etc/kubernetes/pki/etcd/ca.crt --cert=/etc/kubernetes/pki/etcd/healthcheck-client.crt --key=/etc/kubernetes/pki/etcd/healthcheck-client.key get /registry/secrets/starfleet/launch-code --print-value-only | grep -a -o 'warp-nine-launch'
```

A copy of the original API server and etcd manifests is in `/opt/training/backup` on the node. Keep your own backups outside `/etc/kubernetes/manifests`.

## Common pitfalls

> [!WARNING]
> Query etcd with read commands only. A write bypasses validation. This environment shares the kernel of the host, so the node is not a dedicated virtual machine.
