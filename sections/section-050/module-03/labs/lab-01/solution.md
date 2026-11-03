---
draft: true
exam_objectives:
- Verify platform binaries before deploying
---
# Identify The Forged Signature Solution

This walkthrough solves the task step by step. Run the first block to select the environment:

```sh
export KUBECONFIG="$(astrona kubeconfig ats-031-lab-050-03-01)"
test "$(kubectl config current-context)" = "kind-astro-ats-031-lab-050-03-01" || exit 1
CONTROL=astro-ats-031-lab-050-03-01-control-plane
WORKER=astro-ats-031-lab-050-03-01-worker
```

Verify the GPG signature with the keyring file and read the exit status:

```sh
podman exec -w /var/lib/training-release/signed/lab $CONTROL gpg --no-default-keyring --keyring ./publisher.gpg --verify gpg-notes.txt.asc gpg-notes.txt
echo "exit status: $?"
```

Verify the cosign signature with the public key. The transparency log is skipped because the node has no network path to it:

```sh
podman exec -w /var/lib/training-release/signed/lab $CONTROL cosign verify-blob --key cosign.pub --signature cosign-notes.txt.sig --insecure-ignore-tlog=true cosign-notes.txt
echo "exit status: $?"
```

One command reports a good signature or `Verified OK` with exit status 0. The other reports a failure with a nonzero status. The file of the failing check is the forged one. Write its name, replacing `<tool>` with `gpg` or `cosign`:

```sh
podman exec $CONTROL sh -c 'echo <tool> > /var/lib/training-release/signed/lab/result.txt'
podman exec $CONTROL cat /var/lib/training-release/signed/lab/result.txt
```

After recording your result, remove the independent lab with `astrona destroy ats-031-lab-050-03-01`.

## Common pitfalls

> [!WARNING]
> The gpg warning that the key is not certified is not a failure; read the exit status. If your cosign version rejects a flag, check its `--help` output. Do not edit the files to make a check pass.
