---
exam_objectives:
- Protect node metadata and endpoints
---
# Turn On NodeRestriction And Remove A Protected Node Label Solution

## Inspect the starting state

Start with the flags of the API server. The kubelet starts the API server from its manifest file on the control plane node, so read the two flags that matter there:

```sh
podman exec astro-ats-031-lab-040-03-05-control-plane grep -E 'authorization-mode|admission-plugins' /etc/kubernetes/manifests/kube-apiserver.yaml
```

It prints only the line `- --authorization-mode=Node,RBAC`. There is no `--enable-admission-plugins` line. The node authorizer is on, so the kubelet credential may read and update only its own Node object. The authorizer does not look at labels. Without `NodeRestriction`, nothing stops the kubelet from setting any label on its own node.

Now test the worker kubelet's credential directly. The command runs `kubectl` inside the worker node container with the kubelet's kubeconfig file. The option `--dry-run=server` sends the request through authorization and admission, but the API server does not store the change:

```sh
podman exec astro-ats-031-lab-040-03-05-worker kubectl --kubeconfig /etc/kubernetes/kubelet.conf label node astro-ats-031-lab-040-03-05-worker node-restriction.kubernetes.io/lab-check=open --dry-run=server
kubectl get node astro-ats-031-lab-040-03-05-worker --show-labels | tr ',' '\n' | grep node-restriction
```

The first command succeeds: the worker credential may set a protected label on its own node. The second shows the label `node-restriction.kubernetes.io/dedicated=payments` on the worker.

## Turn the plugin back on

The kubelet watches `/etc/kubernetes/manifests` and restarts a static pod when its file changes. A half-written file or an extra backup file in that directory can break the pod, so edit a copy in another directory and move it back in one step. The `sed` command adds the flag on a new line after the authorization line, with the same indentation:

```sh
podman exec astro-ats-031-lab-040-03-05-control-plane mkdir -p /etc/kubernetes/edit
podman exec astro-ats-031-lab-040-03-05-control-plane cp -p /etc/kubernetes/manifests/kube-apiserver.yaml /etc/kubernetes/edit/kube-apiserver.yaml
podman exec astro-ats-031-lab-040-03-05-control-plane sed -i 's|^\( *\)- --authorization-mode=Node,RBAC$|&\n\1- --enable-admission-plugins=NodeRestriction|' /etc/kubernetes/edit/kube-apiserver.yaml
podman exec astro-ats-031-lab-040-03-05-control-plane grep -A1 authorization-mode /etc/kubernetes/edit/kube-apiserver.yaml
podman exec astro-ats-031-lab-040-03-05-control-plane mv /etc/kubernetes/edit/kube-apiserver.yaml /etc/kubernetes/manifests/kube-apiserver.yaml
```

The `grep` line shows `- --authorization-mode=Node,RBAC` and, under it, `- --enable-admission-plugins=NodeRestriction`. Check it before the `mv`, because the kubelet acts on the file as soon as it is in place.

The kubelet now stops the old API server and starts a new one. For some seconds `kubectl` gets no answer. Wait until it answers again:

```sh
until kubectl get --raw=/readyz >/dev/null 2>&1; do sleep 3; done
```

## Remove the protected label

The plugin stops new writes, but it does not undo the label that is already on the node. Remove it with your own administrator credential. The `-` after the key removes the label:

```sh
kubectl label node astro-ats-031-lab-040-03-05-worker node-restriction.kubernetes.io/dedicated-
```

## Verify

Send the two writes again with the worker credential:

```sh
podman exec astro-ats-031-lab-040-03-05-worker kubectl --kubeconfig /etc/kubernetes/kubelet.conf label node astro-ats-031-lab-040-03-05-worker node-restriction.kubernetes.io/lab-check=open --dry-run=server
podman exec astro-ats-031-lab-040-03-05-worker kubectl --kubeconfig /etc/kubernetes/kubelet.conf label node astro-ats-031-lab-040-03-05-worker node-role.kubernetes.io/control-plane= --dry-run=server
kubectl get nodes
```

Both writes now fail with a `Forbidden` error that names the node user `system:node:astro-ats-031-lab-040-03-05-worker`. `NodeRestriction` refuses both, because a kubelet may not set labels with the prefix `node-restriction.kubernetes.io/`, nor most labels under `kubernetes.io`, such as the role label `node-role.kubernetes.io/control-plane`. A node that could give itself the control plane role label could attract workloads meant for the control plane. If a write still succeeds, the old API server may still be running; wait a few seconds and send it again. Both nodes are `Ready`. Then submit.

After recording your result, remove the independent lab with `astrona destroy ats-031-lab-040-03-05`.

## Common pitfalls

> [!WARNING]
> Turning the plugin on does not remove a label that a node already set, so check the labels of every node after you fix the API server. A `kubectl auth can-i` test with `--as=system:node:<name>` shows only the authorizer decision; admission plugins do not run for it, so test a real write with `--dry-run=server`. Keep `Node` in `--authorization-mode`: `NodeRestriction` limits node writes, and the node authorizer limits node reads.
