---
draft: true
exam_objectives:
- Verify platform binaries before deploying
---
# Find The Binary That Fails Verification Solution

This walkthrough solves the task step by step. Run the first block to select the environment:

```sh
export KUBECONFIG="$(astrona kubeconfig ats-031-lab-050-02-01)"
test "$(kubectl config current-context)" = "kind-astro-ats-031-lab-050-02-01" || exit 1
CONTROL=astro-ats-031-lab-050-02-01-control-plane
WORKER=astro-ats-031-lab-050-02-01-worker
```

Open a shell in the control plane node container and list the staged files:

```sh
podman exec $CONTROL ls -l /var/lib/training-release/k8s/lab
```

Check each binary against its checksum file. The checksum file holds only the digest, so build the line `digest`, two spaces, `file name` for `sha256sum --check`:

```sh
podman exec -w /var/lib/training-release/k8s/lab $CONTROL sh -c 'for f in kubectl kubeadm kubelet; do if echo "$(cat $f.sha256)  $f" | sha256sum --check --status; then echo "$f: OK"; else echo "$f: FAILED"; fi; done'
```

Exactly one name is followed by `FAILED`. Write that name into the result file, replacing `<name>` with it:

```sh
podman exec $CONTROL sh -c 'echo <name> > /var/lib/training-release/k8s/lab/result.txt'
podman exec $CONTROL cat /var/lib/training-release/k8s/lab/result.txt
```

The last command prints only the file name. Then submit.

After recording your result, remove the independent lab with `astrona destroy ats-031-lab-050-02-01`.

## Common pitfalls

> [!WARNING]
> Do not recompute the checksum file from the binary: that check always passes and proves nothing. Do not run the failing binary. Write only the file name, without a path.
