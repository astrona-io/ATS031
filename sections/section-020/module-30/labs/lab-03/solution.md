# Recover A Broken Controller Manager Static Pod — Solution

You solve this lab by removing one broken line from the controller manager manifest and setting its mode. Keep `astrona submit --watch` running in a second terminal: it grades the lab again and again while you work and records nothing. Each check below turns green as you finish its task.

## Step 1: look at the starting state

When a static pod fails, the API often shows little, because the pod object is only a mirror that the kubelet creates. The container runtime on the node has the real state. List the controller manager containers, including the ones that have stopped, and read the log of the newest one:

```sh
sudo crictl ps -a --name kube-controller-manager
sudo crictl logs "$(sudo crictl ps -a --name kube-controller-manager -q | head -n 1)"
```

The containers have the state `Exited`, and the log ends with an error about an unknown flag: `--profilling`. The flag name has a typing mistake, so the program stops at once. Check the mode of the manifest too:

```sh
sudo stat -c '%a %U:%G %n' /etc/kubernetes/manifests/kube-controller-manager.yaml
```

The mode is `644`, so every user on the node can read the manifest. The night edit changed the mode as well.

## Step 2: remove the broken flag (check `manifest-flag-removed`)

The kubelet watches `/etc/kubernetes/manifests` and starts every file in it as a static pod. Edit a copy in a work directory outside that folder, so that the kubelet never reads a half-written file. Remove only the broken line:

```sh
sudo mkdir -p /etc/kubernetes/edit
sudo cp -p /etc/kubernetes/manifests/kube-controller-manager.yaml /etc/kubernetes/edit/kube-controller-manager.yaml
sudo sed -i '/--profilling=false/d' /etc/kubernetes/edit/kube-controller-manager.yaml
sudo diff /opt/training/backup/kube-controller-manager.yaml /etc/kubernetes/edit/kube-controller-manager.yaml
```

The `diff` command prints nothing when the repaired copy matches the backup line for line.

## Step 3: set the mode and move the copy back (check `manifest-mode-kept`)

`cp -p` keeps the mode and owner of the file, so the copy still has mode `644`. Set mode `600` on the copy, then move it back in one step:

```sh
sudo chmod 600 /etc/kubernetes/edit/kube-controller-manager.yaml
sudo mv /etc/kubernetes/edit/kube-controller-manager.yaml /etc/kubernetes/manifests/kube-controller-manager.yaml
sudo stat -c '%a %U:%G %n' /etc/kubernetes/manifests/kube-controller-manager.yaml
sudo ls /etc/kubernetes/manifests
```

`stat` prints `600 root:root /etc/kubernetes/manifests/kube-controller-manager.yaml`, and the folder holds only the four manifests.

## Step 4: check the running controller manager (check `controller-manager-running`)

The kubelet starts a new controller manager from the changed file. Wait until its pod is ready:

```sh
kubectl -n kube-system wait --for=condition=Ready "pod/kube-controller-manager-$(hostname)" --timeout=120s
sudo crictl ps --name kube-controller-manager
```

The `wait` command prints `pod/kube-controller-manager-<node> condition met`, and the container is `Running`.

## Step 5: submit

When `astrona submit --watch` shows every check passing, stop it and run `astrona submit`. This grades the lab for real, ends the attempt and removes the lab.

## Common pitfalls

> [!WARNING]
> A file such as `kube-controller-manager.yaml.bak` inside `/etc/kubernetes/manifests` is read by the kubelet as one more static pod, and the grader accepts only the four manifests there.
>
> Copying the backup or moving a file without setting the mode leaves a mode wider than `600`.
>
> `kubectl logs` on the mirror pod can show an older container; read the newest log with `crictl`.
