---
draft: true
exam_objectives:
- Use CIS benchmark to review the security configuration of Kubernetes components
  (etcd, kubelet, kubedns, kubeapi)
---
# Summary

etcd stores every object of the cluster, including all Secrets, under keys that start with `/registry`. The API server is the only component that should connect to it, over the client port `2379`. etcd members replicate over the peer port `2380`. kubeadm gives etcd its own certificate authority in `/etc/kubernetes/pki/etcd`, and the API server connects with a client certificate that this authority signed.

The benchmark checks the TLS flags in the etcd static pod manifest. The certificate and key flags must be set for clients and for peers. `--client-cert-auth` and `--peer-client-cert-auth` must be `true`, so that a client without a valid certificate cannot read data. `--auto-tls` and `--peer-auto-tls` must not be `true`, and their default is `false`. A review compares the manifest with the command of the running pod and proves the client check with a request made with and without a certificate. A single control plane node has no peer traffic, so the peer flags are checked in the files only.

The data directory `/var/lib/etcd` must have mode `700`, because a copy of its files restores the whole cluster. The ownership recommendation of a dedicated `etcd` user applies only when etcd runs as that user. kubeadm runs etcd as `root` by default, so a reviewer records that finding with its reason instead of changing the owner alone. Snapshots and backups hold the same data and need the same protection.

A client with a valid certificate reads etcd directly and sees Secret values in plain text. TLS and file permissions do not change that. Encryption at rest changes it: the API server reads an `EncryptionConfiguration` named by `--encryption-provider-config`, the first provider encrypts every new write, and the file must be mounted into the API server pod. Existing Secrets stay plain text until they are written again, so a reviewer reads every Secret through the API server and replaces it unchanged. The proof is the prefix `k8s:enc:aescbc:v1:` on the value read from etcd.

Key facts to remember:

- Only the API server needs an etcd client certificate.
- A missing `--auto-tls` flag means `false`, which is the secure state.
- Data directory mode `700`; the owner recommendation depends on the process user.
- The first provider encrypts; `identity` last keeps old values readable.
- Check encryption in etcd, not only in the flag.

<!-- astrona:playground:destroy -->
