---
exam_objectives:
- Use CIS benchmark to review the security configuration of Kubernetes components
  (etcd, kubelet, kubedns, kubeapi)
---
# Enable NodeRestriction Solution

Open a shell on the lab VM (virtual machine) and check that kubectl uses this lab's cluster:

```sh
astrona ssh astro-ats-031-lab-020-03-05
kubectl config current-context
```

The second command prints `kubernetes-admin@astro-ats-031-lab-020-03-05`. You are logged in as the `student` user, which has a kubeconfig file for the cluster. A kubeconfig file tells `kubectl` which cluster to use and which credentials to send. Node files and processes belong to root, so run node commands with `sudo`. They change only the lab VM, not your own computer.

## Show what a kubelet can do now

Every kubelet signs in to the API server with its own client certificate, as the user `system:node:<node-name>`. The node keeps this identity in `/etc/kubernetes/kubelet.conf`, and the node image includes `kubectl`. Labels with the prefix `node-restriction.kubernetes.io/` are meant for administrators: a `nodeSelector` on such a label places sensitive pods only on nodes that an administrator chose. Use the kubelet identity to set such a label on the node:

```sh
sudo kubectl --kubeconfig /etc/kubernetes/kubelet.conf label node "astro-ats-031-lab-020-03-05" node-restriction.kubernetes.io/lab-check=kubelet --overwrite
```

The command prints `node/... labeled`. The Node authorizer lets a kubelet update its own Node object, and nothing checks which labels it writes. Remove the label again with your administrator credentials:

```sh
kubectl label node "astro-ats-031-lab-020-03-05" node-restriction.kubernetes.io/lab-check-
```

## Enable the plugin

The `NodeRestriction` admission plugin closes this gap: it lets a kubelet change only its own Node object and the pods bound to its node, and it rejects labels with the `node-restriction.kubernetes.io/` prefix. Read the admission flags of the running API server:

```sh
sudo ps -eo args | grep '^kube-apiserver' | tr ' ' '\n' | grep -e 'admission-plugins'
```

The flag is `--enable-admission-plugins=LimitRanger`. Add `NodeRestriction` to the same list, so that `LimitRanger` stays. The kubelet watches `/etc/kubernetes/manifests` and starts every file in it as a static pod. Edit a copy in a work directory outside that folder, check the copy, and move it back in one step, so that the kubelet never reads a half-written file:

```sh
sudo mkdir -p /etc/kubernetes/edit
sudo cp -p /etc/kubernetes/manifests/kube-apiserver.yaml /etc/kubernetes/edit/kube-apiserver.yaml
sudo sed -i 's|--enable-admission-plugins=LimitRanger|--enable-admission-plugins=LimitRanger,NodeRestriction|' /etc/kubernetes/edit/kube-apiserver.yaml
sudo grep -e 'admission-plugins' /etc/kubernetes/edit/kube-apiserver.yaml
sudo mv /etc/kubernetes/edit/kube-apiserver.yaml /etc/kubernetes/manifests/kube-apiserver.yaml
```

Wait until the new API server answers, then check the flag of the running process:

```sh
for attempt in $(seq 1 60); do
  if sudo ps -eo args | grep '^kube-apiserver ' | grep -q -e 'NodeRestriction' && kubectl --request-timeout=3s get --raw=/readyz >/dev/null 2>&1; then echo "new flag visible and API server ready"; break; fi
  sleep 3
done
```

The old API server process can still answer for a few seconds after the `mv`, so the loop waits until the running API server process has the new flag and the API server is ready. It prints `new flag visible and API server ready`. If it ends without that message, run `sudo crictl ps -a --name kube-apiserver` and read the logs of the exited container.

```sh
sudo ps -eo args | grep '^kube-apiserver' | tr ' ' '\n' | grep -e 'admission-plugins'
```

## Prove the restriction

Run the same label request with the node's kubelet identity again:

```sh
sudo kubectl --kubeconfig /etc/kubernetes/kubelet.conf label node "astro-ats-031-lab-020-03-05" node-restriction.kubernetes.io/lab-check=kubelet --overwrite
```

This time the API server rejects the request with a `forbidden` error. The identity, the authorizer and the request are the same as before, so the new admission plugin is what stopped it. The Node authorizer still allows the kubelet to update its own Node object; `NodeRestriction` checks the content of the update and rejects the restricted label.

## Common pitfalls

> [!WARNING]
> Replacing the whole `--enable-admission-plugins` value drops the plugins that were there; add to the list instead. A second `--enable-admission-plugins` flag adds to the first, so read the whole command line. `NodeRestriction` works together with the `Node` authorizer; it does not replace it.
