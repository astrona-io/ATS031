---
exam_objectives:
- Verify platform binaries before deploying
---
# Find The Files That Fail A Checksum Manifest: Solution

Connect to the lab first, so that `kubectl` talks to this lab's cluster and `$node_name` names its control plane node:

```sh
export KUBECONFIG="$(astrona kubeconfig ats-031-lab-050-01-01)"
node_name="astro-ats-031-lab-050-01-01-control-plane"
```

## Check the files against the manifest

`sha256sum --check` reads each line of the manifest, computes the digest of the named file and prints `OK` or `FAILED`. The file names in the manifest have no directory, so run the check in the release directory. The option `-w` of `podman exec` sets the working directory inside the node container.

```sh
podman exec -w /var/lib/fleet-release "$node_name" sha256sum --check SHA256SUMS
```

The output has one line per file. The files with `FAILED` are the answer, and the last line is a warning that counts them. The exit status is 1, because at least one file failed. The sizes and the dates of the files are all normal, so `ls -l` does not show which files changed; only the digest does.

The option `--quiet` prints only the failing lines, which is handy when the manifest is long:

```sh
podman exec -w /var/lib/fleet-release "$node_name" sha256sum --check --quiet SHA256SUMS
```

## Compute the digest of fleet-agent

`sha256sum` without `--check` prints the digest of a file and its name. Keep only the digest:

```sh
agent_digest=$(podman exec "$node_name" sha256sum /var/lib/fleet-release/fleet-agent | cut -d' ' -f1)
echo "$agent_digest"
```

## Record the result

Put the failing names, separated by commas, in the `failed` key. Replace the example names below with the ones that your check reported:

```sh
kubectl -n starfleet-031-050-01-01 create configmap manifest-check \
  --from-literal=failed=fleet-cli,fleet-sync \
  --from-literal=agent-sha256="$agent_digest"
kubectl -n starfleet-031-050-01-01 get configmap manifest-check -o yaml
```

The grader computes the digests of the files again and compares them with the manifest, so the `failed` list must name exactly the files that fail now.

A manifest check proves only that the files match the manifest. In this lab the manifest is correct by agreement. In a real release you first check the signature of the manifest, because an attacker who changes a file can also change its line in an unsigned manifest.
