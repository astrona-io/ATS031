# Harden The Controller Manager And Scheduler — Solution

You solve this lab by adding one flag to two static pod manifests and tightening the manifest modes. Keep `astrona submit --watch` running in a second terminal: it grades the lab again and again while you work and records nothing. Each check below turns green as you finish its task.

## Step 1: look at the starting state

The controller manager and the scheduler have the same `--profiling` flag as the API server, with the same default `true`. Read the flags of both running processes and the modes of the manifests:

```sh
sudo ps -eo args | grep -e '^kube-controller-manager' -e '^kube-scheduler' | tr ' ' '\n' | grep -e '^kube-' -e '--profiling'
sudo sh -c "stat -c '%a %U:%G %n' /etc/kubernetes/manifests/*"
```

The first command prints the two program names and no `--profiling` flag. The second shows mode `644` on `kube-controller-manager.yaml` and `kube-scheduler.yaml`.

The kubelet watches `/etc/kubernetes/manifests` and starts every file in it as a static pod, a pod that the kubelet runs from a file on the node. Edit each manifest as a copy in a work directory outside that folder, and move it back in one step, so that the kubelet never reads a half-written file.

## Step 2: disable controller manager profiling (check `controller-manager-profiling`)

```sh
sudo mkdir -p /etc/kubernetes/edit
sudo cp -p /etc/kubernetes/manifests/kube-controller-manager.yaml /etc/kubernetes/edit/kube-controller-manager.yaml
sudo sed -i 's|^\( *\)- kube-controller-manager$|&\n\1- --profiling=false|' /etc/kubernetes/edit/kube-controller-manager.yaml
sudo mv /etc/kubernetes/edit/kube-controller-manager.yaml /etc/kubernetes/manifests/kube-controller-manager.yaml
```

The `sed` expression adds the new flag on the line after the program name, with the same indentation.

## Step 3: disable scheduler profiling (check `scheduler-profiling`)

```sh
sudo cp -p /etc/kubernetes/manifests/kube-scheduler.yaml /etc/kubernetes/edit/kube-scheduler.yaml
sudo sed -i 's|^\( *\)- kube-scheduler$|&\n\1- --profiling=false|' /etc/kubernetes/edit/kube-scheduler.yaml
sudo mv /etc/kubernetes/edit/kube-scheduler.yaml /etc/kubernetes/manifests/kube-scheduler.yaml
```

## Step 4: restrict the manifests (check `manifest-permissions`)

`cp -p` kept the old mode, so the two moved files still have mode `644`. Set mode `600` on every manifest. A mode change does not restart a static pod:

```sh
sudo sh -c 'chmod 600 /etc/kubernetes/manifests/*.yaml'
sudo sh -c "stat -c '%a %U:%G %n' /etc/kubernetes/manifests/*"
```

Every line now starts with `600 root:root`.

## Step 5: test the running processes

Wait for the kubelet to start the new pods, then read the flags again:

```sh
kubectl -n kube-system wait --for=condition=Ready "pod/kube-controller-manager-$(hostname)" "pod/kube-scheduler-$(hostname)" --timeout=180s
sudo ps -eo args | grep -e '^kube-controller-manager' -e '^kube-scheduler' | tr ' ' '\n' | grep -e '^kube-' -e '--profiling'
```

The `wait` command prints `condition met` for both pods, and both programs now show `--profiling=false`.

## Step 6: submit

When `astrona submit --watch` shows every check passing, stop it and run `astrona submit`. This grades the lab for real, ends the attempt and removes the lab.

## Common pitfalls

> [!WARNING]
> The grader reads the running processes, not the manifests, and needs each pod ready. A flag in the file does nothing until the new pod runs.
>
> A manifest moved in from a copy keeps the copy mode, so check the mode after every edit. The grader checks every file in `/etc/kubernetes/manifests`, so a backup left there with mode `644` also fails.
