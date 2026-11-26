# Restrict Control Plane Kubeconfig And Key Files

A file scan of the control plane node reports that some credential files in `/etc/kubernetes` and `/etc/kubernetes/pki` can be read by every local user (mode `644`). The scan does not say which ones. Find them and close them.

1. Give every kubeconfig file `/etc/kubernetes/*.conf` mode `600` or stricter and the owner `root:root`.
2. Give every private key file (`*.key`) in `/etc/kubernetes/pki` mode `600` or stricter and the owner `root:root`.
3. Give every private key file in `/etc/kubernetes/pki/etcd` mode `600` or stricter and the owner `root:root`.

Node files belong to root; use `sudo`. Do not change certificate files (`*.crt`); they stay at mode `644` and owner `root:root`. The API server must stay ready and both `probe` replicas must stay available.
