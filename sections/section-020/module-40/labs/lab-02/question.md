# Record How The API Server Connects To etcd

Before a review of the control plane, the security team wants to know exactly how the API server reaches etcd and which files prove its identity. Record the answers in the ConfigMap `etcd-connection` in namespace `starfleet-031-020-04-02`. Read each value from the running `kube-apiserver` process, not from memory.

1. Key `servers`: the value of `--etcd-servers`.
2. Keys `client-certificate` and `client-key`: the paths in `--etcd-certfile` and `--etcd-keyfile`.
3. Key `ca-file`: the path in `--etcd-cafile`.

Node files and processes belong to root; use `sudo`.

Do not change the cluster: leave the control plane manifests and the kubelet configuration as they are.
