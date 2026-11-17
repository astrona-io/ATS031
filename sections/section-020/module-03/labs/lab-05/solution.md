---
exam_objectives:
- Use CIS benchmark to review the security configuration of Kubernetes components
  (etcd, kubelet, kubedns, kubeapi)
---
# Enable NodeRestriction Solution

Connect to this lab from a host shell. The command `astrona kubeconfig` prints the path of the lab's kubeconfig, the file that tells `kubectl` which cluster to use and which credentials to send. The two variables hold the names of the node containers: `node_name` is the control plane node and `worker_name` is the worker node.

```sh
export KUBECONFIG="$(astrona kubeconfig ats-031-lab-020-03-05)"
test "$(kubectl config current-context)" = "kind-astro-ats-031-lab-020-03-05" || exit 1
node_name="astro-ats-031-lab-020-03-05-control-plane"
worker_name="astro-ats-031-lab-020-03-05-worker"
```

Run node commands as `podman exec "$node_name" ...` or `podman exec "$worker_name" ...`. They change only the node containers of this lab, not your own computer.

## Show what a kubelet can do now

Every kubelet signs in to the API server with its own client certificate, as the user `system:node:<node-name>`. The worker node keeps this identity in `/etc/kubernetes/kubelet.conf`, and the node image includes `kubectl`. Labels with the prefix `node-restriction.kubernetes.io/` are meant for administrators: a `nodeSelector` on such a label places sensitive pods only on nodes that an administrator chose. Use the kubelet identity to set such a label on the worker node:

```sh
podman exec "$worker_name" kubectl --kubeconfig /etc/kubernetes/kubelet.conf label node "$worker_name" node-restriction.kubernetes.io/lab-check=kubelet --overwrite
```

The command prints `node/... labeled`. The Node authorizer lets a kubelet update its own Node object, and nothing checks which labels it writes. Remove the label again with your administrator credentials:

```sh
kubectl label node "$worker_name" node-restriction.kubernetes.io/lab-check-
```

## Enable the plugin

The `NodeRestriction` admission plugin closes this gap: it lets a kubelet change only its own Node object and the pods bound to its node, and it rejects labels with the `node-restriction.kubernetes.io/` prefix. Read the admission flags of the running API server:

```sh
podman exec "$node_name" ps -eo args | grep '^kube-apiserver' | tr ' ' '\n' | grep -e 'admission-plugins'
```

The flag is `--enable-admission-plugins=LimitRanger`. Add `NodeRestriction` to the same list, so that `LimitRanger` stays. The kubelet watches `/etc/kubernetes/manifests` and starts every file in it as a static pod. Edit a copy in a work directory outside that folder, check the copy, and move it back in one step, so that the kubelet never reads a half-written file:

```sh
podman exec "$node_name" mkdir -p /etc/kubernetes/edit
podman exec "$node_name" cp -p /etc/kubernetes/manifests/kube-apiserver.yaml /etc/kubernetes/edit/kube-apiserver.yaml
podman exec "$node_name" sed -i 's|--enable-admission-plugins=LimitRanger|--enable-admission-plugins=LimitRanger,NodeRestriction|' /etc/kubernetes/edit/kube-apiserver.yaml
podman exec "$node_name" grep -e 'admission-plugins' /etc/kubernetes/edit/kube-apiserver.yaml
podman exec "$node_name" mv /etc/kubernetes/edit/kube-apiserver.yaml /etc/kubernetes/manifests/kube-apiserver.yaml
```

Wait until the new API server answers, then check the flag of the running process:

```sh
kubectl get --raw=/readyz
podman exec "$node_name" ps -eo args | grep '^kube-apiserver' | tr ' ' '\n' | grep -e 'admission-plugins'
```

## Prove the restriction

Run the same label request with the worker's kubelet identity again:

```sh
podman exec "$worker_name" kubectl --kubeconfig /etc/kubernetes/kubelet.conf label node "$worker_name" node-restriction.kubernetes.io/lab-check=kubelet --overwrite
```

This time the API server rejects the request with a `forbidden` error. The identity, the authorizer and the request are the same as before, so the new admission plugin is what stopped it. The Node authorizer still allows the kubelet to update its own Node object; `NodeRestriction` checks the content of the update and rejects the restricted label.

## Common pitfalls

> [!WARNING]
> Replacing the whole `--enable-admission-plugins` value drops the plugins that were there; add to the list instead. A second `--enable-admission-plugins` flag adds to the first, so read the whole command line. `NodeRestriction` works together with the `Node` authorizer; it does not replace it.
