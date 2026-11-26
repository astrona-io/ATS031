# Restrict The Kubelet Service Files And Turn On Certificate Rotation

A CIS benchmark review of the node found that the systemd files of the `kubelet` service have mode `644` and that certificate rotation is turned off. Find the service files with `systemctl`, not from memory.

1. The kubelet unit file (`FragmentPath` of the `kubelet` service) has mode `600` or stricter and the owner `root:root`.
2. Every drop-in file of the `kubelet` service (`DropInPaths`) has mode `600` or stricter and the owner `root:root`.
3. The effective kubelet configuration has `rotateCertificates` set to `true`.

Node files belong to root; use `sudo`. A copy of the original kubelet configuration is in `/opt/training/backup/kubelet-config.yaml`.

The node must stay `Ready`, and both `probe` replicas must stay available.
