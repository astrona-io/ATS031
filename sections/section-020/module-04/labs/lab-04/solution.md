---
exam_objectives:
- Use CIS benchmark to review the security configuration of Kubernetes components
  (etcd, kubelet, kubedns, kubeapi)
---
# Restrict The etcd Data Directory Solution

Connect to this lab from a host shell. The command `astrona kubeconfig` prints the path of the lab's kubeconfig, the file that tells `kubectl` which cluster to use and which credentials to send. The two variables hold the names of the node containers: `node_name` is the control plane node and `worker_name` is the worker node.

```sh
export KUBECONFIG="$(astrona kubeconfig ats-031-lab-020-04-04)"
test "$(kubectl config current-context)" = "kind-astro-ats-031-lab-020-04-04" || exit 1
node_name="astro-ats-031-lab-020-04-04-control-plane"
worker_name="astro-ats-031-lab-020-04-04-worker"
```

Run node commands as `podman exec "$node_name" ...` or `podman exec "$worker_name" ...`. They change only the node containers of this lab, not your own computer.

## Find the data directory

The benchmark checks the directory that etcd really uses, so read it from the running process instead of guessing the default:

```sh
podman exec "$node_name" sh -c 'tr "\0" "\n" < /proc/$(pgrep -n etcd)/cmdline' | grep -e '^--data-dir'
```

The value is `/var/lib/etcd` on a kubeadm cluster. Now read the mode, the owner and the user that runs etcd:

```sh
podman exec "$node_name" stat -c '%a %U:%G %n' /var/lib/etcd
podman exec "$node_name" ps -o user= -p "$(podman exec "$node_name" pgrep -n etcd)"
```

The mode is `755`, so every user on the node can list the directory. The owner is `root:root`, and etcd runs as `root`. The benchmark text asks for the owner `etcd:etcd`, which fits only when etcd runs as a user called `etcd`. Here the owner must stay `root:root`, or etcd can no longer write its data.

## Restrict the mode

Change only the mode, then check it and the health of etcd through the API server:

```sh
podman exec "$node_name" chmod 700 /var/lib/etcd
podman exec "$node_name" stat -c '%a %U:%G %n' /var/lib/etcd
kubectl get --raw='/readyz/etcd'
```

The mode is `700`, and the last command prints `ok`.

## Record the facts

Create the ConfigMap with the two values you read:

```sh
kubectl -n starfleet-031-020-04-04 create configmap etcd-process --from-literal=data-dir=/var/lib/etcd --from-literal=user=root
kubectl -n starfleet-031-020-04-04 get configmap etcd-process -o yaml
```

## Common pitfalls

> [!WARNING]
> A `chown etcd:etcd` on a cluster where etcd runs as `root` is not needed, and on a node without an `etcd` user it fails. `chmod -R` also changes the files inside the directory; the finding is about the directory itself. Read the data directory from the process, because a cluster can use another path.
