---
exam_objectives:
- Verify platform binaries before deploying
---
# Find The Binary That Fails Verification

Allow about 6 minutes for the tasks.

The release team of the `starfleet` cluster staged seven control plane binaries on the control plane node. Each binary has a published checksum. One binary was changed after its checksum was published. Its size and its modification time did not change.

## Connect to the lab

Use a shell on your own machine. The kubeconfig file holds the address and the credentials of this lab's cluster, and `kubectl` uses it.

```sh
export KUBECONFIG="$(astrona kubeconfig ats-031-lab-050-02-03)"
test "$(kubectl config current-context)" = "kind-astro-ats-031-lab-050-02-03" || exit 1
node_name="astro-ats-031-lab-050-02-03-control-plane"
```

The node of a `kind` cluster is a container on your machine. Run a command inside it with `podman exec "$node_name" <command>`. If your machine uses Docker, write `docker exec` instead.

## Tasks

The binaries are in `/var/lib/node-bundle` on the control plane node. Each one has a file with the same name and the suffix `.sha256`, which holds only the published digest.

1. Verify every binary against its published digest.
2. Create the ConfigMap `failing-binary` in the namespace `starfleet-031-050-02-03` with the key `name`, set to the file name of the one binary that fails verification.

Do not change or run the staged binaries. The changed binary is chosen at random each time the lab starts.
