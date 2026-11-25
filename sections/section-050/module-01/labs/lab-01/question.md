---
exam_objectives:
- Verify platform binaries before deploying
---
# Find The Files That Fail A Checksum Manifest

Allow about 8 minutes for the tasks.

The fleet build team copied six release files to the control plane node of the `starfleet` cluster. During the copy, some of the files changed. Find them before anyone installs them.

## Connect to the lab

Use a shell on your own machine. The kubeconfig file holds the address and the credentials of this lab's cluster, and `kubectl` uses it.

```sh
export KUBECONFIG="$(astrona kubeconfig ats-031-lab-050-01-01)"
test "$(kubectl config current-context)" = "kind-astro-ats-031-lab-050-01-01" || exit 1
node_name="astro-ats-031-lab-050-01-01-control-plane"
```

The node of a `kind` cluster is a container on your machine. Run a command inside it with `podman exec "$node_name" <command>`. If your machine uses Docker, write `docker exec` instead.

## Tasks

The directory `/var/lib/fleet-release` on the control plane node holds six files and a `SHA256SUMS` manifest. The manifest has one line for each file, in the form `digest`, two spaces, file name. The manifest itself is correct.

1. Check every file against `SHA256SUMS` and find the files that fail.
2. Compute the current SHA-256 digest of `fleet-agent`, whether it passes or fails.
3. Create the ConfigMap `manifest-check` in the namespace `starfleet-031-050-01-01` with two keys:
   - `failed`: the names of all failing files, separated by commas, for example `fleet-cli,fleet-sync`.
   - `agent-sha256`: the 64-character digest from step 2.

Do not change the files or the manifest. The failing files are chosen at random each time the lab starts.
