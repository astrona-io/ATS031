---
exam_objectives:
- Use CIS benchmark to review the security configuration of Kubernetes components
  (etcd, kubelet, kubedns, kubeapi)
---
# Harden The Controller Manager And Scheduler Solution

Connect to this lab from a host shell. The command `astrona kubeconfig` prints the path of the lab's kubeconfig, the file that tells `kubectl` which cluster to use and which credentials to send. The two variables hold the names of the node containers: `node_name` is the control plane node and `worker_name` is the worker node.

```sh
export KUBECONFIG="$(astrona kubeconfig ats-031-lab-020-03-06)"
test "$(kubectl config current-context)" = "kind-astro-ats-031-lab-020-03-06" || exit 1
node_name="astro-ats-031-lab-020-03-06-control-plane"
worker_name="astro-ats-031-lab-020-03-06-worker"
```

Run node commands as `podman exec "$node_name" ...` or `podman exec "$worker_name" ...`. They change only the node containers of this lab, not your own computer.

## Read the current state

The controller manager and the scheduler have the same `--profiling` flag as the API server, with the same default `true`. Read the flags of both running processes and the modes of the manifests:

```sh
podman exec "$node_name" ps -eo args | grep -e '^kube-controller-manager' -e '^kube-scheduler' | tr ' ' '\n' | grep -e '^kube-' -e '--profiling'
podman exec "$node_name" sh -c "stat -c '%a %U:%G %n' /etc/kubernetes/manifests/*"
```

The first command prints the two program names and no `--profiling` flag. The second shows mode `644` on two manifests.

## Disable profiling

Each component has its own manifest, so edit each one the safe way. The kubelet watches `/etc/kubernetes/manifests` and starts every file in it as a static pod. Edit a copy in a work directory outside that folder, check the copy, and move it back in one step, so that the kubelet never reads a half-written file:

```sh
podman exec "$node_name" mkdir -p /etc/kubernetes/edit
podman exec "$node_name" cp -p /etc/kubernetes/manifests/kube-controller-manager.yaml /etc/kubernetes/edit/kube-controller-manager.yaml
podman exec "$node_name" sed -i 's|^\( *\)- kube-controller-manager$|&\n\1- --profiling=false|' /etc/kubernetes/edit/kube-controller-manager.yaml
podman exec "$node_name" mv /etc/kubernetes/edit/kube-controller-manager.yaml /etc/kubernetes/manifests/kube-controller-manager.yaml
podman exec "$node_name" cp -p /etc/kubernetes/manifests/kube-scheduler.yaml /etc/kubernetes/edit/kube-scheduler.yaml
podman exec "$node_name" sed -i 's|^\( *\)- kube-scheduler$|&\n\1- --profiling=false|' /etc/kubernetes/edit/kube-scheduler.yaml
podman exec "$node_name" mv /etc/kubernetes/edit/kube-scheduler.yaml /etc/kubernetes/manifests/kube-scheduler.yaml
```

The `sed` expression adds the new flag on the line after the program name, with the same indentation.

## Restrict the manifests

`cp -p` kept the old mode, so the two moved files still have mode `644`. Set mode `600` on every manifest. A mode change does not restart a static pod:

```sh
podman exec "$node_name" sh -c 'chmod 600 /etc/kubernetes/manifests/*.yaml'
podman exec "$node_name" sh -c "stat -c '%a %U:%G %n' /etc/kubernetes/manifests/*"
```

## Verify the running processes

Wait about a minute for the kubelet to start the new pods. Then read the flags again and check the pods:

```sh
podman exec "$node_name" ps -eo args | grep -e '^kube-controller-manager' -e '^kube-scheduler' | tr ' ' '\n' | grep -e '^kube-' -e '--profiling'
kubectl -n kube-system get pods -l tier=control-plane
```

Both programs now show `--profiling=false`, and every control plane pod is running.

## Common pitfalls

> [!WARNING]
> Editing a manifest in place with `sed -i` inside `/etc/kubernetes/manifests` can leave a temporary file that the kubelet reads. A manifest moved in from a copy keeps the copy mode, so check the mode after every edit. The controller manager and the scheduler have no `/readyz` path of the API server; check their pods.
