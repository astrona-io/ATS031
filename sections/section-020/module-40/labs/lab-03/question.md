# Require Client Certificates On etcd

A review of the control plane found that etcd accepts connections without a client certificate. Any process that reaches port `2379` on the control plane node can read and write the cluster data. etcd runs as a static pod from `/etc/kubernetes/manifests/etcd.yaml`.

1. Run etcd with `--client-cert-auth=true` on its client port.
2. Run etcd with `--peer-client-cert-auth=true` on its peer port.
3. A request to `https://127.0.0.1:2379/health` without a client certificate is refused, and the API server stays ready.

Node files belong to root; use `sudo`. A copy of the original manifest is in `/opt/training/backup/etcd.yaml`.

Keep every backup outside `/etc/kubernetes/manifests`.
