---
exam_objectives:
- Verify platform binaries before deploying
---
# Verify The Running kubelet Against A Release Checksum

Allow about 12 minutes for the tasks.

An audit of the `starfleet` cluster found that the kubelet on the worker node may not be the official build. The kubelet is the node agent that starts the containers of each Pod on a node. Check the kubelet that actually runs, not the file you expect it to run from.

## Connect to the lab

Use a shell on your own machine. The kubeconfig file holds the address and the credentials of this lab's cluster, and `kubectl` uses it.

```sh
export KUBECONFIG="$(astrona kubeconfig ats-031-lab-050-02-05)"
test "$(kubectl config current-context)" = "kind-astro-ats-031-lab-050-02-05" || exit 1
worker_name="astro-ats-031-lab-050-02-05-worker"
```

The node of a `kind` cluster is a container on your machine. Run a command inside it with `podman exec "$worker_name" <command>`. If your machine uses Docker, write `docker exec` instead.

## Tasks

The worker node holds the published digests of the kubelet in `/var/lib/kubelet-release/<version>/bin/linux/<architecture>/kubelet.sha256`. Each file holds only the digest.

1. Find the version of the running kubelet and the path of the binary that the running kubelet process was started from.
2. Compute the SHA-256 digest of that binary.
3. Compare it with the published digest for that version and the architecture of the worker.
4. Create the ConfigMap `kubelet-review` in the namespace `starfleet-031-050-02-05` with four keys:
   - `version`: the version of the running kubelet, for example `v1.35.0`.
   - `path`: the full path of the binary of the running kubelet process.
   - `sha256`: the digest of that binary.
   - `result`: `match` if it equals the published digest, otherwise `mismatch`.

Do not restart the kubelet and do not change any file on the node. The path and the result are chosen at random each time the lab starts.
