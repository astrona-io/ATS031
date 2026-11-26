# Enable NodeRestriction — Solution

You solve this lab by adding one admission plugin to the API server manifest. Keep `astrona submit --watch` running in a second terminal: it grades the lab again and again while you work and records nothing. Each check below turns green as you finish its task.

## Step 1: look at the starting state

Every kubelet signs in to the API server with its own client certificate, as the user `system:node:<node-name>`. The node keeps this identity in `/etc/kubernetes/kubelet.conf`, and the node image includes `kubectl`. Labels with the prefix `node-restriction.kubernetes.io/` are meant for administrators: a `nodeSelector` on such a label places sensitive pods only on nodes that an administrator chose. Use the kubelet identity to set such a label on the node:

```sh
sudo kubectl --kubeconfig /etc/kubernetes/kubelet.conf label node "$(hostname)" node-restriction.kubernetes.io/lab-check=kubelet --overwrite
```

The command prints `node/<node> labeled`. The Node authorizer lets a kubelet update its own Node object, and nothing checks which labels it writes. Remove the label again with your administrator credentials:

```sh
kubectl label node "$(hostname)" node-restriction.kubernetes.io/lab-check-
```

Read the admission flags of the running API server:

```sh
sudo ps -eo args | grep '^kube-apiserver' | tr ' ' '\n' | grep -e 'admission-plugins'
```

The flag is `--enable-admission-plugins=LimitRanger`.

## Step 2: enable the plugin (check `noderestriction-enabled`)

The `NodeRestriction` admission plugin lets a kubelet change only its own Node object and the pods bound to its node, and it rejects labels with the `node-restriction.kubernetes.io/` prefix. The kubelet watches `/etc/kubernetes/manifests` and starts every file in it as a static pod. Edit a copy in a work directory outside that folder, so that the kubelet never reads a half-written file:

```sh
sudo mkdir -p /etc/kubernetes/edit
sudo cp -p /etc/kubernetes/manifests/kube-apiserver.yaml /etc/kubernetes/edit/kube-apiserver.yaml
sudo sed -i 's|--enable-admission-plugins=LimitRanger|--enable-admission-plugins=LimitRanger,NodeRestriction|' /etc/kubernetes/edit/kube-apiserver.yaml
sudo grep -e 'admission-plugins' /etc/kubernetes/edit/kube-apiserver.yaml
```

The `grep` prints `- --enable-admission-plugins=LimitRanger,NodeRestriction` and no `--disable-admission-plugins` line. Move the copy back in one step:

```sh
sudo mv /etc/kubernetes/edit/kube-apiserver.yaml /etc/kubernetes/manifests/kube-apiserver.yaml
```

Wait until the new API server answers:

```sh
for attempt in $(seq 1 60); do
  if sudo ps -eo args | grep '^kube-apiserver ' | grep -q -e 'NodeRestriction' && kubectl --request-timeout=3s get --raw=/readyz >/dev/null 2>&1; then echo "new flag visible and API server ready"; break; fi
  sleep 3
done
```

The old API server process can still answer for a few seconds after the `mv`, so the loop waits until the running process has the new flag and the API server is ready. It prints `new flag visible and API server ready`. If it ends without that message, run `sudo crictl ps -a --name kube-apiserver` and read the logs of the exited container with `sudo crictl logs <CONTAINER_ID>`.

## Step 3: check the plugin list (check `admission-plugins-kept`)

```sh
sudo ps -eo args | grep '^kube-apiserver' | tr ' ' '\n' | grep -e 'admission-plugins'
```

The running process has `--enable-admission-plugins=LimitRanger,NodeRestriction`, so `LimitRanger` stays enabled.

## Step 4: test the restriction (check `node-label-denied`)

Run the same label request with the node's kubelet identity again:

```sh
sudo kubectl --kubeconfig /etc/kubernetes/kubelet.conf label node "$(hostname)" node-restriction.kubernetes.io/lab-check=kubelet --overwrite
```

This time the API server rejects the request with a `forbidden` error. The identity, the authorizer and the request are the same as before, so the new admission plugin is what stopped it.

## Step 5: submit

When `astrona submit --watch` shows every check passing, stop it and run `astrona submit`. This grades the lab for real, ends the attempt and removes the lab.

## Common pitfalls

> [!WARNING]
> Replacing the whole `--enable-admission-plugins` value with `NodeRestriction` drops `LimitRanger`; add to the list instead.
>
> `NodeRestriction` in `--disable-admission-plugins` turns it off again, whatever the enable list says.
>
> The label request must fail with a `forbidden` error. A request that fails for another reason, such as a wrong kubeconfig path, does not count.
