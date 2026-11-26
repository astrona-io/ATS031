# Record A Manual Audit Of The API Server And etcd

The auditor does not trust a report that only copies default values. The API server and etcd on the control plane node run with settings chosen when the lab started, and some differ from the kubeadm defaults. Read the real values and record them in the ConfigMap `manual-audit` in namespace `starfleet-031-020-01-03`.

1. Record the API server values: key `apiserver-authorization-mode` with the value of `--authorization-mode` as written in the flag, and key `apiserver-profiling` with `true` or `false`, the effective profiling setting (when the flag is not set, the default applies).
2. Record key `etcd-client-cert-auth` with `true` or `false`, the effective value of the etcd flag `--client-cert-auth`.
3. Record key `etcd-data-dir-mode` with the octal mode of `/var/lib/etcd` as `stat -c %a` prints it (for example `700`).

Node files belong to root; use `sudo`. Do not change any setting of the cluster.
