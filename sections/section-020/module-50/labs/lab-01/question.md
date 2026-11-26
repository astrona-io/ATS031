# Secure Kubelet Authentication And Authorization

A review of the node found that the kubelet API on port `10250` answers requests without credentials and allows every action. The kubelet reads its configuration from `/var/lib/kubelet/config.yaml`.

1. The effective kubelet configuration has `authentication.anonymous.enabled: false`.
2. The effective kubelet configuration has `authorization.mode: Webhook`.
3. A request without credentials on the node to `https://<node-ip>:10250/pods` returns HTTP `401`.

Node files belong to root; use `sudo`. A copy of the original kubelet configuration is in `/opt/training/backup/kubelet-config.yaml`.

The node must stay `Ready`, and both `probe` replicas must stay available.
