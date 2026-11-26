# Remediate Five Kubelet Benchmark Findings

A CIS benchmark review of the node found two kubelet files with mode `644`, `rotateCertificates` set to `false`, no useful `streamingConnectionIdleTimeout` and no `tlsMinVersion`. The kubelet reads its configuration from `/var/lib/kubelet/config.yaml`.

1. `/var/lib/kubelet/config.yaml` and `/etc/kubernetes/kubelet.conf` have mode `600` or stricter and the owner `root:root`.
2. The effective kubelet configuration has `rotateCertificates` set to `true`.
3. The effective `streamingConnectionIdleTimeout` is `5m0s`.
4. The effective `tlsMinVersion` is `VersionTLS12` or `VersionTLS13`.

Node files belong to root; use `sudo`. A copy of the original kubelet configuration is in `/opt/training/backup/kubelet-config.yaml`.

The node must stay `Ready`, and both `probe` replicas must stay available.
