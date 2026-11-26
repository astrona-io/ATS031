# Remove A Kubelet Flag That Overrides The Configuration File

The file `/var/lib/kubelet/config.yaml` on the node sets `authorization.mode: Webhook`, but the kubelet still allows every request. A command-line flag overrides the file.

1. `/var/lib/kubelet/kubeadm-flags.env` sets no `--authorization-mode` flag.
2. The running kubelet process has no `--authorization-mode` flag.
3. The effective kubelet configuration has `authorization.mode` set to `Webhook`.

Node files belong to root; use `sudo`. A copy of the kubelet files is in `/opt/training/backup`.

Keep every other flag in `kubeadm-flags.env`. The node must stay `Ready`, and both `probe` replicas must stay available.
