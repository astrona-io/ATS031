# Restrict The Kubelet Service Files And Turn On Certificate Rotation — Solution

You solve this lab with two `chmod` commands, one field in the kubelet configuration file and a kubelet restart. Keep `astrona submit --watch` running in a second terminal: it grades the lab again and again while you work and records nothing. Each check below turns green as you finish its task.

## Step 1: look at the starting state

systemd starts the kubelet from a unit file, and drop-in files add settings to it. kubeadm puts its own drop-in file next to the unit. Ask systemd which files it uses, instead of guessing the paths:

```sh
sudo systemctl show kubelet -p FragmentPath -p DropInPaths
```

The output names the unit file in `FragmentPath` and one or more drop-in files in `DropInPaths`. Read their modes:

```sh
sudo sh -c 'stat -c "%a %U:%G %n" $(systemctl show kubelet -p FragmentPath -p DropInPaths --value)'
```

Each file has mode `644`, so every user on the node can read how the kubelet starts. The benchmark asks for `600` or stricter.

## Step 2: restrict the unit file (check `service-file-modes`)

Change the mode of the file that `FragmentPath` names:

```sh
sudo sh -c 'chmod 600 $(systemctl show kubelet -p FragmentPath --value)'
```

systemd only reads these files; a mode change needs no restart.

## Step 3: restrict the drop-in files (check `drop-in-file-modes`)

Change the mode of every file that `DropInPaths` names, then read all modes again:

```sh
sudo sh -c 'chmod 600 $(systemctl show kubelet -p DropInPaths --value)'
sudo sh -c 'stat -c "%a %U:%G %n" $(systemctl show kubelet -p FragmentPath -p DropInPaths --value)'
```

Every line now starts with `600 root:root`.

## Step 4: turn on certificate rotation (check `rotate-certificates`)

The kubelet proves its identity to the API server with a client certificate. With `rotateCertificates: true`, the kubelet asks for a new certificate before the old one expires. Read the effective value first:

```sh
kubectl get --raw "/api/v1/nodes/$(hostname)/proxy/configz" | python3 -m json.tool | grep rotateCertificates
```

The command prints nothing, because the endpoint leaves out a field with the value `false`. The kubelet stops at start when a key appears twice, so delete the key before you add it again, then restart the kubelet:

```sh
sudo sed -i '/^rotateCertificates:/d' /var/lib/kubelet/config.yaml
sudo sh -c "printf '\nrotateCertificates: true\n' >> /var/lib/kubelet/config.yaml"
sudo systemctl restart kubelet
```

The kubelet reads its configuration only when it starts.

## Step 5: test the result

Read the effective configuration through the API server. The `configz` endpoint returns the values that the running kubelet really uses, after all sources are merged:

```sh
kubectl get --raw "/api/v1/nodes/$(hostname)/proxy/configz" | python3 -m json.tool | grep rotateCertificates
kubectl get node "$(hostname)"
```

The first command prints a line with `"rotateCertificates": true`, and the node is `Ready`. If the field is still missing, wait a few seconds and run the command again.

## Step 6: submit

When `astrona submit --watch` shows every check passing, stop it and run `astrona submit`. This grades the lab for real, ends the attempt and removes the lab.

## Common pitfalls

> [!WARNING]
> The drop-in directory can hold more than one file. Take the list from `systemctl show`, because the grader checks every file that systemd names.
>
> A mode such as `640` still lets the group read the file; the grader accepts only `600` or stricter, with the owner `root:root`.
>
> A missing field in `configz` means `false` for `rotateCertificates`. A changed file without a kubelet restart changes nothing.
