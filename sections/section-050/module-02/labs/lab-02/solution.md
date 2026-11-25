---
exam_objectives:
- Verify platform binaries before deploying
---
# Verify Downloads With sha256sum --check: Solution

Connect to the lab first, so that `kubectl` talks to this lab's cluster and `$node_name` names its control plane node:

```sh
export KUBECONFIG="$(astrona kubeconfig ats-031-lab-050-02-02)"
node_name="astro-ats-031-lab-050-02-02-control-plane"
```

## Build the check file

The release site publishes one `.sha256` file per binary, and it holds only the digest. `sha256sum --check` needs a different format: the digest, two spaces and the file name. Open a shell in the download directory on the node, then write one line for each download:

```sh
podman exec -it -w /var/lib/k8s-downloads "$node_name" bash
for tool in kubectl kubeadm kubelet; do
  printf '%s  %s\n' "$(cat $tool.sha256)" "$tool"
done > SHA256SUMS
cat SHA256SUMS
```

The loop reads every digest from the published file. It never runs `sha256sum` on the download itself: a digest computed from the file you want to check always matches, so it proves nothing.

## Run the strict check

`--strict` makes `sha256sum` fail on any line that is not in the check format, so a broken line cannot be skipped in silence. Run the check inside the same shell and print the exit status right after it:

```sh
sha256sum --check --strict SHA256SUMS; echo "exit status $?"
exit
```

When every file matches, each line ends with `OK` and the exit status is `0`. When one file was changed, its line ends with `FAILED`, `sha256sum` prints a warning that one computed checksum did not match, and the exit status is `1`.

## Record the result

Use the exit status and the failing name that you saw. The example records a failed `kubeadm`:

```sh
kubectl -n starfleet-031-050-02-02 create configmap download-check \
  --from-literal=exit-status=1 --from-literal=failed=kubeadm
```

If every download passed, use `exit-status=0` and `failed=none`. The grader reads each `.sha256` file and `SHA256SUMS`, computes the digests itself and compares the result with the ConfigMap.
