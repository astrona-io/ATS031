---
exam_objectives:
- Verify platform binaries before deploying
---
# Pick The Release Files For A Node

Allow about 6 minutes for the tasks.

The worker node of the `starfleet` cluster needs a new `kubeadm`. An offline copy of the Kubernetes release site sits on the control plane node. Pick the exact file for the worker and note its published digest.

## Connect to the lab

Use a shell on your own machine. The kubeconfig file holds the address and the credentials of this lab's cluster, and `kubectl` uses it.

```sh
export KUBECONFIG="$(astrona kubeconfig ats-031-lab-050-02-01)"
test "$(kubectl config current-context)" = "kind-astro-ats-031-lab-050-02-01" || exit 1
node_name="astro-ats-031-lab-050-02-01-control-plane"
```

The node of a `kind` cluster is a container on your machine. Run a command inside it with `podman exec "$node_name" <command>`. If your machine uses Docker, write `docker exec` instead.

## Tasks

The mirror is in `/var/lib/k8s-mirror` on the control plane node. It uses the same layout as the release site: `release/<version>/bin/<os>/<architecture>/<name>`, with a `<name>.sha256` file next to each binary.

1. Find the current stable version that the mirror publishes.
2. Find the CPU architecture of the worker node `astro-ats-031-lab-050-02-01-worker`, in the form that the release paths use (`amd64` or `arm64`).
3. Create the ConfigMap `release-pick` in the namespace `starfleet-031-050-02-01` with two keys:
   - `path`: the path of the Linux `kubeadm` file for that version and architecture, relative to the mirror, in the form `release/<version>/bin/linux/<architecture>/kubeadm`.
   - `sha256`: the published digest of that file, from its `.sha256` file.

The stable version is chosen at random each time the lab starts.
