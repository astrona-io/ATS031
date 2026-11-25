---
exam_objectives:
- Use CIS benchmark to review the security configuration of Kubernetes components
  (etcd, kubelet, kubedns, kubeapi)
---
# Guided Practice: Inspect etcd And Its Protection

This ungraded playground is one virtual machine (VM) that runs a single-node Kubernetes v1.35 cluster built with kubeadm, the standard tool that installs a cluster on a Linux machine. The node `astro-ats-031-playground-020-04` is the control plane and also runs your pods. etcd, the key-value database of the cluster, runs on it as a static pod, a pod that the kubelet starts from a file in `/etc/kubernetes/manifests`. The Secret `launch-code` in the `starfleet` namespace exists and no encryption configuration is set. The permissions of the etcd data directory are wider than the benchmark allows.

<!-- astrona:playground:renew -->

Open a shell on the node. You log in as the `student` user, which has `sudo` and a kubeconfig file for the cluster. A kubeconfig file tells kubectl, the Kubernetes command-line tool, which cluster to use and which credentials to send.

```sh
astrona ssh astro-ats-031-playground-020-04
kubectl config current-context
```

The second command prints `kubernetes-admin@astro-ats-031-playground-020-04`. Commands that use `sudo` change only this VM. They do not touch your own computer.

## Inspect

Read the TLS flags and the data directory in the etcd manifest, then the mode of the data directory. Both paths are readable only by `root`, so the commands use `sudo`:

```sh
sudo grep -e 'client-cert-auth' -e 'auto-tls' -e 'data-dir' /etc/kubernetes/manifests/etcd.yaml
sudo stat -c '%a %U:%G %n' /var/lib/etcd
```

The output at the start of the playground:

```text
    - --client-cert-auth=true
    - --data-dir=/var/lib/etcd
    - --peer-client-cert-auth=true
755 root:root /var/lib/etcd
```

Both `client-cert-auth` flags are `true` and no `auto-tls` flag is set, which is the secure state. The mode `755` is the finding: the benchmark asks for `700`.

The node has no `etcdctl` binary, so read the Secret through the `etcdctl` client in the etcd pod. The value is binary, so the `grep` prints only a readable word:

```sh
kubectl -n kube-system exec etcd-astro-ats-031-playground-020-04 -- etcdctl --endpoints=https://127.0.0.1:2379 --cacert=/etc/kubernetes/pki/etcd/ca.crt --cert=/etc/kubernetes/pki/etcd/healthcheck-client.crt --key=/etc/kubernetes/pki/etcd/healthcheck-client.key get /registry/secrets/starfleet/launch-code --print-value-only | grep -a -o 'warp-nine-launch'
```

The command prints `warp-nine-launch` twice: once from the Secret data and once from the `kubectl.kubernetes.io/last-applied-configuration` annotation. The value is stored in etcd as plain text.

## Suggested exercises

These exercises use only the node and the commands above.

1. Set the data directory to mode `700` with `sudo chmod 700 /var/lib/etcd` and run `sudo kube-bench run --check 1.1.11,1.1.12`. Check `1.1.11` passes. Check `1.1.12` still fails, because the node has no `etcd` user and etcd runs as `root`.
2. Enable encryption at rest for Secrets with an `EncryptionConfiguration` and the `--encryption-provider-config` flag of the API server. The API server restarts after the manifest edit; on this node that took between 40 and 70 seconds.
3. Rewrite all Secrets with `kubectl get secrets --all-namespaces -o json | kubectl replace -f -` and read `launch-code` from etcd again. The value now starts with `k8s:enc:aescbc:v1:key1`.

A copy of the original API server and etcd manifests and of the kubelet configuration is in `/opt/training/backup` on the node. Copy a file back with `sudo cp` to return to the starting state. Keep your own backups outside `/etc/kubernetes/manifests`, because the kubelet starts a pod from every file in that directory that is not hidden.

## Common pitfalls

> [!WARNING]
> Query etcd with read commands only: a write with `etcdctl put` or `del` bypasses validation and can break the cluster. Run node commands with `sudo`, or they fail with `Permission denied` for the wrong reason. A broken edit to the API server manifest stops the API server, so `kubectl` fails until you fix the file or copy the backup back.
