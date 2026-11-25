---
exam_objectives:
- Use CIS benchmark to review the security configuration of Kubernetes components
  (etcd, kubelet, kubedns, kubeapi)
---
# Harden The Controller Manager And Scheduler Solution

Open a shell on the lab VM (virtual machine) and check that kubectl uses this lab's cluster:

```sh
astrona ssh astro-ats-031-lab-020-03-06
kubectl config current-context
```

The second command prints `kubernetes-admin@astro-ats-031-lab-020-03-06`. You are logged in as the `student` user, which has a kubeconfig file for the cluster. A kubeconfig file tells `kubectl` which cluster to use and which credentials to send. Node files and processes belong to root, so run node commands with `sudo`. They change only the lab VM, not your own computer.

## Read the current state

The controller manager and the scheduler have the same `--profiling` flag as the API server, with the same default `true`. Read the flags of both running processes and the modes of the manifests:

```sh
sudo ps -eo args | grep -e '^kube-controller-manager' -e '^kube-scheduler' | tr ' ' '\n' | grep -e '^kube-' -e '--profiling'
sudo sh -c "stat -c '%a %U:%G %n' /etc/kubernetes/manifests/*"
```

The first command prints the two program names and no `--profiling` flag. The second shows mode `644` on two manifests.

## Disable profiling

Each component has its own manifest, so edit each one the safe way. The kubelet watches `/etc/kubernetes/manifests` and starts every file in it as a static pod. Edit a copy in a work directory outside that folder, check the copy, and move it back in one step, so that the kubelet never reads a half-written file:

```sh
sudo mkdir -p /etc/kubernetes/edit
sudo cp -p /etc/kubernetes/manifests/kube-controller-manager.yaml /etc/kubernetes/edit/kube-controller-manager.yaml
sudo sed -i 's|^\( *\)- kube-controller-manager$|&\n\1- --profiling=false|' /etc/kubernetes/edit/kube-controller-manager.yaml
sudo mv /etc/kubernetes/edit/kube-controller-manager.yaml /etc/kubernetes/manifests/kube-controller-manager.yaml
sudo cp -p /etc/kubernetes/manifests/kube-scheduler.yaml /etc/kubernetes/edit/kube-scheduler.yaml
sudo sed -i 's|^\( *\)- kube-scheduler$|&\n\1- --profiling=false|' /etc/kubernetes/edit/kube-scheduler.yaml
sudo mv /etc/kubernetes/edit/kube-scheduler.yaml /etc/kubernetes/manifests/kube-scheduler.yaml
```

The `sed` expression adds the new flag on the line after the program name, with the same indentation.

## Restrict the manifests

`cp -p` kept the old mode, so the two moved files still have mode `644`. Set mode `600` on every manifest. A mode change does not restart a static pod:

```sh
sudo sh -c 'chmod 600 /etc/kubernetes/manifests/*.yaml'
sudo sh -c "stat -c '%a %U:%G %n' /etc/kubernetes/manifests/*"
```

## Verify the running processes

Wait about a minute for the kubelet to start the new pods. Then read the flags again and check the pods:

```sh
sudo ps -eo args | grep -e '^kube-controller-manager' -e '^kube-scheduler' | tr ' ' '\n' | grep -e '^kube-' -e '--profiling'
kubectl -n kube-system get pods -l tier=control-plane
```

Both programs now show `--profiling=false`, and every control plane pod is running.

## Common pitfalls

> [!WARNING]
> Editing a manifest in place with `sed -i` inside `/etc/kubernetes/manifests` can leave a temporary file that the kubelet reads. A manifest moved in from a copy keeps the copy mode, so check the mode after every edit. The controller manager and the scheduler have no `/readyz` path of the API server; check their pods.
