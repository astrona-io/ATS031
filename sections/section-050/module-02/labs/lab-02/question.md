---
exam_objectives:
- Verify platform binaries before deploying
---
# Verify Downloads With sha256sum --check

Allow about 8 minutes for the tasks.

An operator of the `starfleet` cluster downloaded `kubectl`, `kubeadm` and `kubelet` to the control plane node, each with the `.sha256` file that the release site publishes next to it. Check all three downloads in one run of `sha256sum --check`.

## Connect to the lab

Use a shell on your own machine. The kubeconfig file holds the address and the credentials of this lab's cluster, and `kubectl` uses it.

```sh
export KUBECONFIG="$(astrona kubeconfig ats-031-lab-050-02-02)"
test "$(kubectl config current-context)" = "kind-astro-ats-031-lab-050-02-02" || exit 1
node_name="astro-ats-031-lab-050-02-02-control-plane"
```

The node of a `kind` cluster is a container on your machine. Run a command inside it with `podman exec "$node_name" <command>`. If your machine uses Docker, write `docker exec` instead.

## Tasks

The downloads are in `/var/lib/k8s-downloads` on the control plane node. Each `.sha256` file holds only a 64-character digest, with no file name.

1. Create `/var/lib/k8s-downloads/SHA256SUMS` in the format that `sha256sum --check` reads: one line per download, with the published digest, two spaces and the file name without a directory.
2. Run `sha256sum --check --strict SHA256SUMS` in that directory and note its exit status.
3. Create the ConfigMap `download-check` in the namespace `starfleet-031-050-02-02` with two keys:
   - `exit-status`: the exit status of the check, as a number.
   - `failed`: the name of the download that failed the check, or `none` if every download passed.

Take each digest from its `.sha256` file, never from the downloaded file itself. Do not change the downloads. Each start of the lab decides at random whether one download is damaged.
