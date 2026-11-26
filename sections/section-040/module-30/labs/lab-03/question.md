# Remove A Runtime Socket Mount

The Deployment `image-scanner` in `dock-031-040-03-03` mounts the host directory `/run/containerd` at `/host/run/containerd` and runs as user id 0. With the containerd socket, a root process can ask the runtime to start a container that mounts the whole node.

1. Remove the container runtime host path from the `image-scanner` pod template.
2. The running `image-scanner` pod mounts no runtime path and cannot see `containerd.sock`.
3. The `scanner` container sets `runAsNonRoot: true`, and its process does not run as user id 0.

Keep the `scratch` volume at `/scratch` and the `settings` ConfigMap volume at `/etc/scanner`, and do not change the Deployment `log-shipper`.
