# Turn On NodeRestriction And Remove A Protected Node Label — Solution

You solve this lab by adding one flag to the API server manifest on the control plane node and removing one label from the worker node. Keep `astrona submit --watch` running in a second terminal: it grades the lab again and again while you work and records nothing. Each check below turns green as you finish its task.

## Step 1: look at the starting state

Start with the flags of the API server. The kubelet starts the API server from its manifest file on the control plane node, so read the two flags that matter there. Use `docker` instead of `podman` if your machine uses Docker:

```sh
podman exec astro-ats-031-lab-040-03-05-control-plane grep -E 'authorization-mode|admission-plugins' /etc/kubernetes/manifests/kube-apiserver.yaml
```

It prints only the line `- --authorization-mode=Node,RBAC`. There is no `--enable-admission-plugins` line. The node authorizer is on, so the kubelet credential may read and update only its own Node object. The authorizer does not look at labels. Without `NodeRestriction`, nothing stops the kubelet from setting any label on its own node.

Now test the credential of the worker kubelet directly. The command runs `kubectl` inside the worker node container with the kubeconfig file of the kubelet. The option `--dry-run=server` sends the request through authorization and admission, but the API server does not store the change:

```sh
podman exec astro-ats-031-lab-040-03-05-worker kubectl --kubeconfig /etc/kubernetes/kubelet.conf label node astro-ats-031-lab-040-03-05-worker node-restriction.kubernetes.io/lab-check=open --dry-run=server
kubectl get node astro-ats-031-lab-040-03-05-worker --show-labels | tr ',' '\n' | grep node-restriction
```

The first command succeeds: the worker credential may set a protected label on its own node. The second shows the label `node-restriction.kubernetes.io/dedicated=payments` on the worker.

## Step 2: turn the plugin on (check `admission-plugin`)

The kubelet watches `/etc/kubernetes/manifests` and restarts a static pod when its file changes. A half-written file or an extra backup file in that directory can break the pod, so edit a copy in another directory and move it back in one step:

```sh
podman exec astro-ats-031-lab-040-03-05-control-plane mkdir -p /etc/kubernetes/edit
podman exec astro-ats-031-lab-040-03-05-control-plane cp -p /etc/kubernetes/manifests/kube-apiserver.yaml /etc/kubernetes/edit/kube-apiserver.yaml
```

In the copy `/etc/kubernetes/edit/kube-apiserver.yaml`, add a new line after `- --authorization-mode=Node,RBAC`, with the same indentation, so the two lines read:

```yaml
    - --authorization-mode=Node,RBAC
    - --enable-admission-plugins=NodeRestriction
```

The `sed` command below makes exactly that edit. Check the result, then move the file back:

```sh
podman exec astro-ats-031-lab-040-03-05-control-plane sed -i 's|^\( *\)- --authorization-mode=Node,RBAC$|&\n\1- --enable-admission-plugins=NodeRestriction|' /etc/kubernetes/edit/kube-apiserver.yaml
podman exec astro-ats-031-lab-040-03-05-control-plane grep -A1 authorization-mode /etc/kubernetes/edit/kube-apiserver.yaml
podman exec astro-ats-031-lab-040-03-05-control-plane mv /etc/kubernetes/edit/kube-apiserver.yaml /etc/kubernetes/manifests/kube-apiserver.yaml
```

The `grep` command prints the two lines shown above. Check them before the `mv`, because the kubelet acts on the file as soon as it is in place.

The kubelet now stops the old API server and starts a new one. For some seconds `kubectl` gets no answer. Wait until it answers again, then read the flag from the running pod:

```sh
until kubectl get --raw=/readyz >/dev/null 2>&1; do sleep 3; done
kubectl -n kube-system get pod kube-apiserver-astro-ats-031-lab-040-03-05-control-plane -o yaml | grep -E 'authorization-mode|admission-plugins'
```

The output shows both flags.

## Step 3: test the node writes (check `node-writes-refused`)

Send two writes with the worker credential:

```sh
podman exec astro-ats-031-lab-040-03-05-worker kubectl --kubeconfig /etc/kubernetes/kubelet.conf label node astro-ats-031-lab-040-03-05-worker node-restriction.kubernetes.io/lab-check=open --dry-run=server
podman exec astro-ats-031-lab-040-03-05-worker kubectl --kubeconfig /etc/kubernetes/kubelet.conf label node astro-ats-031-lab-040-03-05-worker node-role.kubernetes.io/control-plane= --dry-run=server
```

Both writes fail with a `Forbidden` error that names the node user `system:node:astro-ats-031-lab-040-03-05-worker`. `NodeRestriction` refuses both, because a kubelet may not set labels with the prefix `node-restriction.kubernetes.io/`, nor most labels under `kubernetes.io`, such as the role label `node-role.kubernetes.io/control-plane`. A node that could give itself the control plane role label could attract workloads meant for the control plane. If a write still succeeds, the old API server may still be running; wait a few seconds and send it again.

## Step 4: remove the protected label (check `protected-label-removed`)

The plugin stops new writes, but it does not undo the label that is already on the node. Remove it with your own administrator credential. The `-` after the key removes the label:

```sh
kubectl label node astro-ats-031-lab-040-03-05-worker node-restriction.kubernetes.io/dedicated-
kubectl get nodes
```

`kubectl label` prints `node/astro-ats-031-lab-040-03-05-worker unlabeled`, and both nodes are `Ready`.

## Step 5: submit

When `astrona submit --watch` shows every check passing, stop it and run `astrona submit`. This grades the lab for real, ends the attempt and removes the lab.

## Common pitfalls

> [!WARNING]
> Edit a copy outside `/etc/kubernetes/manifests`. The checks reject any second file in that directory that starts the `kube-apiserver` command, such as a backup copy.
>
> Keep `Node` and `RBAC` in `--authorization-mode`, and do not add `AlwaysAllow`. `NodeRestriction` limits node writes, and the node authorizer limits node reads. The checks also reject `NodeRestriction` in `--disable-admission-plugins`.
>
> Turning the plugin on does not remove a label that a node already set, so check the labels of every node after you fix the API server. A `kubectl auth can-i` test with `--as=system:node:<name>` shows only the authorizer decision; admission plugins do not run for it, so test a real write with `--dry-run=server`.
