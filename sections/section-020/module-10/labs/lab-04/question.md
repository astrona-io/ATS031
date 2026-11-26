# Report The Effective Kubelet Settings

A colleague reviewed only the kubelet configuration file `/var/lib/kubelet/config.yaml` on the node and reported that everything is closed. Check what the kubelet really runs with, and record the **effective** values in the ConfigMap `kubelet-review` in namespace `starfleet-031-020-01-04`.

1. Record key `anonymous-enabled` with `true` or `false` from `authentication.anonymous.enabled`, and key `authorization-mode` with the value of `authorization.mode` (for example `Webhook`).
2. Record key `read-only-port` with the number in `readOnlyPort` (for example `0`).
3. Set the mode of `/var/lib/kubelet/config.yaml` to `600` or stricter, with the owner `root:root`.

Node files belong to root; use `sudo`. Do not change any kubelet setting; the node must stay `Ready`.
