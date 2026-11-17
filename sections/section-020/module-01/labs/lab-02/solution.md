---
exam_objectives:
- Use CIS benchmark to review the security configuration of Kubernetes components
  (etcd, kubelet, kubedns, kubeapi)
---
# Restrict Control Plane Kubeconfig And Key Files Solution

Connect to this lab from a host shell. The command `astrona kubeconfig` prints the path of the lab's kubeconfig, the file that tells `kubectl` which cluster to use and which credentials to send. The two variables hold the names of the node containers: `node_name` is the control plane node and `worker_name` is the worker node.

```sh
export KUBECONFIG="$(astrona kubeconfig ats-031-lab-020-01-02)"
test "$(kubectl config current-context)" = "kind-astro-ats-031-lab-020-01-02" || exit 1
node_name="astro-ats-031-lab-020-01-02-control-plane"
worker_name="astro-ats-031-lab-020-01-02-worker"
```

Run node commands as `podman exec "$node_name" ...` or `podman exec "$worker_name" ...`. They change only the node containers of this lab, not your own computer.

## Find the files with a wide mode

The benchmark asks for mode `600` or stricter on kubeconfig files and private key files, with the owner `root`. A kubeconfig file holds a client certificate and its private key, so anyone who can read it can act as that client. List the mode, the owner and the path of every kubeconfig file on the control plane node:

```sh
podman exec "$node_name" sh -c "stat -c '%a %U:%G %n' /etc/kubernetes/*.conf"
```

The `stat` format prints the mode in octal, then the owner and group, then the path. Look for any line that starts with a mode wider than `600`, such as `644`. Next, use `find` to list the private key files under the `pki` directory, including the `etcd` subdirectory:

```sh
podman exec "$node_name" find /etc/kubernetes/pki -name '*.key' -exec stat -c '%a %U:%G %n' {} +
```

The output shows a few `.key` files with mode `644`. Every other key file already has mode `600`.

## Restrict the modes

The `chmod` command changes the mode of a file. A wildcard needs a shell inside the node, so the first command runs through `sh -c`. The second command lets `find` call `chmod` on every key file it finds:

```sh
podman exec "$node_name" sh -c 'chmod 600 /etc/kubernetes/*.conf'
podman exec "$node_name" find /etc/kubernetes/pki -name '*.key' -exec chmod 600 {} +
```

The components read these files when they start, so no restart is needed. Run the two `stat` commands again. Every line now starts with `600 root:root`. Finally, check that the API server still answers:

```sh
kubectl get --raw=/readyz
```

The command prints `ok`.

## Common pitfalls

> [!WARNING]
> Do not change the owner to a user that the component does not run as; on a kubeadm node the owner stays `root`. Do not restrict certificate files to `600` by habit: they hold no secret, and some clients need to read them. A pattern such as `/etc/kubernetes/pki/*.key` misses the files in `/etc/kubernetes/pki/etcd`.
