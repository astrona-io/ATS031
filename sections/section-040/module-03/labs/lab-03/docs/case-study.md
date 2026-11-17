---
exam_objectives:
- Protect node metadata and endpoints
---
# Starting Environment

The cluster has one control plane node and one worker node. The namespace `dock-031-040-03-03` has two Deployments. The `image-scanner` Deployment runs as user id 0 and mounts the node directory `/run/containerd`, which holds the containerd socket, with a `hostPath` volume. It also mounts an `emptyDir` volume at `/scratch` and the ConfigMap `scanner-settings` at `/etc/scanner`. The `log-shipper` Deployment mounts the node directory `/var/log` read-only; the team reviewed and accepted that mount.
