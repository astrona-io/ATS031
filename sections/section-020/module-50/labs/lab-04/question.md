# Close The Kubelet Read-Only Port And Raise Its TLS Minimum

The kubelet on the node serves the read-only port `10255`, which answers without authentication, and it accepts TLS 1.0 on port `10250`. The kubelet reads its configuration from `/var/lib/kubelet/config.yaml`.

1. The effective kubelet configuration has `readOnlyPort` set to `0`.
2. The effective `tlsMinVersion` is `VersionTLS12` or `VersionTLS13`.
3. A request from the `shuttle` pod in namespace `starfleet-031-020-05-04` to `http://<node-ip>:10255/pods` fails.

Node files belong to root; use `sudo`. A copy of the original kubelet configuration is in `/opt/training/backup/kubelet-config.yaml`.

The node must stay `Ready`, and both `probe` replicas must stay available.
