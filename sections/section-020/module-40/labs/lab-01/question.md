# Enable Encryption At Rest For Secrets

The Secret `launch-code` in namespace `starfleet-031-020-04-01` holds the key `code` with the value `warp-nine-launch`. The API server has no encryption configuration, so etcd stores the value as plain text and anyone with an etcd backup can read it.

1. Create the `EncryptionConfiguration` `/etc/kubernetes/enc/encryption-config.yaml` on the control plane node. For `secrets`, the first provider is `aescbc` with a random 32 byte key, followed by `identity`. The file has mode `600` or stricter.
2. Run the API server with `--encryption-provider-config=/etc/kubernetes/enc/encryption-config.yaml` and mount the directory into its pod.
3. Make etcd store `launch-code` with the prefix `k8s:enc:aescbc:v1:`, so the plain text `warp-nine-launch` no longer appears in etcd. The API still returns `warp-nine-launch` for the key `code`.

Node files belong to root; use `sudo`. A copy of the original API server manifest is in `/opt/training/backup/kube-apiserver.yaml`.

Keep every backup outside `/etc/kubernetes/manifests`.
