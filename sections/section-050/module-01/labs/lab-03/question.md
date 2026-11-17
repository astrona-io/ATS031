---
exam_objectives:
- Verify platform binaries before deploying
---
# Install A Verified Binary Into A Protected Directory

Allow about 12 minutes for the tasks.

Three download caches on the control plane node of the `starfleet` cluster each hold a copy of `fleet-agent`. Only one copy is the signed release. Someone already installed an unverified copy into a directory that any user can write. Replace it with the verified binary and close the directory.

## Connect to the lab

Use a shell on your own machine. The kubeconfig file holds the address and the credentials of this lab's cluster, and `kubectl` uses it.

```sh
export KUBECONFIG="$(astrona kubeconfig ats-031-lab-050-01-03)"
test "$(kubectl config current-context)" = "kind-astro-ats-031-lab-050-01-03" || exit 1
node_name="astro-ats-031-lab-050-01-03-control-plane"
```

The node of a `kind` cluster is a container on your machine. Run a command inside it with `podman exec "$node_name" <command>`. If your machine uses Docker, write `docker exec` instead.

## Tasks

The directory `/var/lib/fleet-release` holds `publisher.pub`, `SHA256SUMS` and `SHA256SUMS.sig`. The signature was made with `openssl dgst -sha256 -sign`. The caches are `/var/cache/fleet/cache-1`, `cache-2` and `cache-3`.

1. Verify the signature of `SHA256SUMS` with `publisher.pub`.
2. Find the cache whose `fleet-agent` matches the authenticated manifest.
3. Install that copy as `/opt/fleet/bin/fleet-agent`, owned by `root:root` with mode `0755`.
4. Make `/opt/fleet` and `/opt/fleet/bin` owned by `root` and not writable by group or others.
5. Check the installed file against the manifest again, at its final location.
6. Create the ConfigMap `install-record` in the namespace `starfleet-031-050-01-03` with two keys:
   - `cache`: the name of the cache that held the genuine copy, for example `cache-2`.
   - `sha256`: the digest from the authenticated manifest.

Do not run any `fleet-agent` copy, and do not change the files in `/var/lib/fleet-release` or the caches. The genuine cache is chosen at random each time the lab starts.
