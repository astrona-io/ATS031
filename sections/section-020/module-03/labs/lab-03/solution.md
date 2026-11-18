---
exam_objectives:
- Use CIS benchmark to review the security configuration of Kubernetes components
  (etcd, kubelet, kubedns, kubeapi)
---
# Recover A Broken Controller Manager Static Pod Solution

Open a shell on the lab VM (virtual machine) and check that kubectl uses this lab's cluster:

```sh
astrona ssh astro-ats-031-lab-020-03-03
kubectl config current-context
```

The second command prints `kubernetes-admin@astro-ats-031-lab-020-03-03`. You are logged in as the `student` user, which has a kubeconfig file for the cluster. A kubeconfig file tells `kubectl` which cluster to use and which credentials to send. Node files and processes belong to root, so run node commands with `sudo`. They change only the lab VM, not your own computer.

## Find why the pod does not start

When a static pod fails, the API often shows little, because the pod object is only a mirror that the kubelet creates. The container runtime on the node has the real state. List the controller manager containers, including the ones that have stopped, and read the log of the newest one:

```sh
sudo crictl ps -a --name kube-controller-manager
sudo crictl logs "$(sudo crictl ps -a --name kube-controller-manager -q | head -n 1)"
```

The containers have the state `Exited`, and the log ends with an error about an unknown flag: `--profilling`. The flag name has a typing mistake, so the program stops at once.

## Repair the manifest

The backup in `/opt/training/backup` is from before the edit. It is safer to remove only the broken line from a copy of the current manifest than to copy the backup back. First check the mode of the current manifest:

```sh
sudo stat -c '%a %U:%G %n' /etc/kubernetes/manifests/kube-controller-manager.yaml
```

The mode is `644`, so every user on the node can read the manifest. The night edit changed the mode as well. `cp -p` keeps the mode and owner of the file, so set mode `600` on the copy before you move it back.

The kubelet watches `/etc/kubernetes/manifests` and starts every file in it as a static pod. Edit a copy in a work directory outside that folder, check the copy, and move it back in one step, so that the kubelet never reads a half-written file:

```sh
sudo mkdir -p /etc/kubernetes/edit
sudo cp -p /etc/kubernetes/manifests/kube-controller-manager.yaml /etc/kubernetes/edit/kube-controller-manager.yaml
sudo sed -i '/--profilling=false/d' /etc/kubernetes/edit/kube-controller-manager.yaml
sudo chmod 600 /etc/kubernetes/edit/kube-controller-manager.yaml
sudo diff /opt/training/backup/kube-controller-manager.yaml /etc/kubernetes/edit/kube-controller-manager.yaml
sudo mv /etc/kubernetes/edit/kube-controller-manager.yaml /etc/kubernetes/manifests/kube-controller-manager.yaml
```

The `diff` command prints nothing when the repaired copy matches the backup line for line.

## Check the result

The kubelet starts a new controller manager within about a minute. Check the container, the pod and the file:

```sh
sudo crictl ps --name kube-controller-manager
kubectl -n kube-system get pod "kube-controller-manager-astro-ats-031-lab-020-03-03"
sudo stat -c '%a %U:%G %n' /etc/kubernetes/manifests/kube-controller-manager.yaml
sudo ls /etc/kubernetes/manifests
```

The container is `Running`, the pod is ready, the mode is `600`, and the folder holds only the four manifests.

## Common pitfalls

> [!WARNING]
> A file such as `kube-controller-manager.yaml.bak` inside `/etc/kubernetes/manifests` is read by the kubelet as one more static pod. `kubectl logs` on the mirror pod can show an older container; read the newest log with `crictl`. Copying a backup without `-p` or moving a file with a wider mode changes the manifest mode.
