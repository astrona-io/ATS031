---
exam_objectives:
- Use CIS benchmark to review the security configuration of Kubernetes components
  (etcd, kubelet, kubedns, kubeapi)
---
# Restrict The Kubelet Service Files And Turn On Certificate Rotation Solution

Open a shell on the lab VM (virtual machine) and check that kubectl uses this lab's cluster:

```sh
astrona ssh astro-ats-031-lab-020-05-05
kubectl config current-context
```

The second command prints `kubernetes-admin@astro-ats-031-lab-020-05-05`. You are logged in as the `student` user, which has a kubeconfig file for the cluster. A kubeconfig file tells `kubectl` which cluster to use and which credentials to send. Node files and processes belong to root, so run node commands with `sudo`. They change only the lab VM, not your own computer.

## Find the unit files

systemd starts the kubelet from a unit file, and drop-in files add settings to it. kubeadm puts its own drop-in file next to the unit. Ask systemd which files it uses, instead of guessing the paths:

```sh
sudo systemctl show kubelet -p FragmentPath -p DropInPaths
```

The output names the unit file in `FragmentPath` and one or more drop-in files in `DropInPaths`. Read their modes:

```sh
sudo sh -c 'stat -c "%a %U:%G %n" $(systemctl show kubelet -p FragmentPath -p DropInPaths --value)'
```

Each file has mode `644`, so every user on the node can read how the kubelet starts. The benchmark asks for `600` or stricter.

## Restrict the files

Change the mode of the same list of files and read it again:

```sh
sudo sh -c 'chmod 600 $(systemctl show kubelet -p FragmentPath -p DropInPaths --value)'
sudo sh -c 'stat -c "%a %U:%G %n" $(systemctl show kubelet -p FragmentPath -p DropInPaths --value)'
```

systemd only reads these files; it does not need a restart for a mode change.

## Turn on certificate rotation

The kubelet proves its identity to the API server with a client certificate. With `rotateCertificates: true`, the kubelet asks for a new certificate before the old one expires. Read the effective value, then replace the key in the file:

```sh
kubectl get --raw "/api/v1/nodes/astro-ats-031-lab-020-05-05/proxy/configz" | python3 -m json.tool | grep rotateCertificates
sudo sed -i '/^rotateCertificates:/d' /var/lib/kubelet/config.yaml
sudo sh -c "printf '\nrotateCertificates: true\n' >> /var/lib/kubelet/config.yaml"
sudo systemctl restart kubelet
```

The first command prints nothing, because the endpoint leaves out a field with the value `false`.

## Check the result

The kubelet reads its configuration only when it starts. Restart it, then read the effective configuration through the API server. The `configz` endpoint returns the values that the running kubelet really uses, after all sources are merged:

```sh
kubectl get --raw "/api/v1/nodes/astro-ats-031-lab-020-05-05/proxy/configz" | python3 -m json.tool | grep rotateCertificates
kubectl get node "astro-ats-031-lab-020-05-05"
```

The value is `true`, and the node is `Ready`.

## Common pitfalls

> [!WARNING]
> The drop-in directory holds more than one file on some nodes; take the list from `systemctl show`, not from memory. A missing field in `configz` means `false` for `rotateCertificates`. Do not set `protectKernelDefaults` on a kind node; the kubelet then refuses to start, because the node shares the kernel of the host.
