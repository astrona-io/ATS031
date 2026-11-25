---
exam_objectives:
- Protect node metadata and endpoints
---
# Remove A Runtime Socket Mount

Allow about 8 minutes for the tasks.

The `image-scanner` in the dock was given the container runtime socket of its node, and it runs as root. The scanner only needs its settings and a scratch directory. Take the socket away and stop it from running as root.

## Starting state

The cluster has one control plane node and one worker node. The namespace `dock-031-040-03-03` has two Deployments:

- `image-scanner` runs as user id 0. A `hostPath` volume mounts the node directory `/run/containerd` at `/host/run/containerd`. That directory holds the containerd socket, the Unix socket that controls every container on the node. The Deployment also mounts an `emptyDir` volume at `/scratch` and the ConfigMap `scanner-settings` at `/etc/scanner`.
- `log-shipper` mounts the node directory `/var/log` read-only. This mount was reviewed and stays.

```sh
export KUBECONFIG="$(astrona kubeconfig ats-031-lab-040-03-03)"
test "$(kubectl config current-context)" = "kind-astro-ats-031-lab-040-03-03" || exit 1
```

Keep this connection selected for the whole task.

## Required result

- The `image-scanner` Deployment mounts no node path of a container runtime (`containerd`, `docker.sock` or `crio`), and the running scanner pod cannot see the containerd socket.
- The `scanner` container sets `runAsNonRoot: true`, in the pod or the container `securityContext`, and its process does not run as user id 0.
- The `scratch` and `settings` volumes stay mounted at `/scratch` and `/etc/scanner`, and the Deployment is available with one ready pod.
- The `log-shipper` Deployment is unchanged.

## Verify the result

The grader reads the Deployments and the running scanner pod. It runs commands inside the scanner pod to look for the socket, to read the user id and to read `/etc/scanner/targets`.
