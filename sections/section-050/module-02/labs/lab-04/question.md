---
exam_objectives:
- Verify platform binaries before deploying
---
# Classify Why Each Download Fails

Allow about 12 minutes for the tasks.

Five download jobs fetched `kubectl` for the control plane node of the `starfleet` cluster. Each job saved the file and the checksum file that came with it. Only one download is ready to install. Find out what went wrong with each of the others.

## Connect to the lab

Use a shell on your own machine. The kubeconfig file holds the address and the credentials of this lab's cluster, and `kubectl` uses it.

```sh
export KUBECONFIG="$(astrona kubeconfig ats-031-lab-050-02-04)"
test "$(kubectl config current-context)" = "kind-astro-ats-031-lab-050-02-04" || exit 1
node_name="astro-ats-031-lab-050-02-04-control-plane"
```

The node of a `kind` cluster is a container on your machine. Run a command inside it with `podman exec "$node_name" <command>`. If your machine uses Docker, write `docker exec` instead.

## Tasks

The control plane node holds two directories:

- `/var/lib/release-index/release/<version>/bin/linux/<architecture>/kubectl.sha256`: the digests that the release team published, for `v1.34.4` and `v1.35.0`, for `amd64` and `arm64`. Trust these digests.
- `/var/lib/k8s-incoming/batch-1` to `batch-5`: each holds the downloaded `kubectl`, the `kubectl.sha256` file that the job saved with it, and a `SOURCE` file with the release path that the job asked for.

1. Give each batch exactly one of these causes:
   - `ok`: the file and its saved checksum both match the published digest for the requested path.
   - `stale-checksum`: the file matches the published digest, but the saved checksum does not.
   - `wrong-arch`: the file is the published `kubectl` of the requested version for the other architecture.
   - `wrong-version`: the file is the published `kubectl` of the other version for the requested architecture.
   - `tampered`: the file matches no published digest.
2. Create the ConfigMap `download-triage` in the namespace `starfleet-031-050-02-04` with these keys:
   - `batch-1` to `batch-5`: the cause of each batch.
   - `rejected`: the name of the tampered batch, for example `batch-3`.

Do not run the downloaded files and do not change them. Each cause appears exactly once, and the order is chosen at random each time the lab starts.
