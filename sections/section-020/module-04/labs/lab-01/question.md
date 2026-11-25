---
exam_objectives:
- Use CIS benchmark to review the security configuration of Kubernetes components
  (etcd, kubelet, kubedns, kubeapi)
---
# Enable Encryption At Rest For Secrets

Allow about 15 minutes for the tasks.

The `starfleet` cluster stores the Secret `launch-code`. A reader of an etcd backup could read the code. Make etcd store Secrets encrypted.

## Starting state

The lab VM runs a one-node Kubernetes cluster built with kubeadm, the standard tool that installs a cluster on a Linux machine. The node `astro-ats-031-lab-020-04-01` is the control plane and also runs the pods. The `starfleet-031-020-04-01` namespace runs two `probe` replicas behind the `probe` Service and a `shuttle` client pod. etcd runs as a static pod on the control plane node. The Secret `launch-code` in the `starfleet-031-020-04-01` namespace holds the key `code` with the value `warp-nine-launch`. The API server has no encryption configuration, so etcd stores the value as plain text. A copy of the API server manifest is in `/opt/training/backup/kube-apiserver.yaml` on the control plane node.

Open a shell on the lab VM (virtual machine) and check that kubectl uses this lab's cluster:

```sh
astrona ssh astro-ats-031-lab-020-04-01
kubectl config current-context
```

The second command prints `kubernetes-admin@astro-ats-031-lab-020-04-01`. You are logged in as the `student` user, which has a kubeconfig file for the cluster. A kubeconfig file tells `kubectl` which cluster to use and which credentials to send. Node files and processes belong to root, so run node commands with `sudo`. They change only the lab VM, not your own computer.

## Required result

- Create an `EncryptionConfiguration` at `/etc/kubernetes/enc/encryption-config.yaml` on the control plane node. For `secrets`, the first provider is `aescbc` with a random 32 byte key, followed by `identity`. The file has mode `600` or stricter.
- The API server runs with `--encryption-provider-config=/etc/kubernetes/enc/encryption-config.yaml` and mounts the directory.
- etcd stores the Secret `launch-code` with the prefix `k8s:enc:aescbc:v1:`, and the plain text `warp-nine-launch` no longer appears in etcd.
- The API still returns the value `warp-nine-launch` for the key `code`.

Keep every backup outside `/etc/kubernetes/manifests`.

## Verify The Result

The grader reads the command line of the running `kube-apiserver` process and the configuration file, reads the stored value of `launch-code` with `etcdctl` in the etcd pod, and reads the Secret through the API.
