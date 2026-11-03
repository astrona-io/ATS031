---
draft: true
exam_objectives:
- Verify platform binaries before deploying
---
# Identify The Forged Signature

Two release notes arrived with detached signatures, one made with GPG and one made with cosign. The `starfleet` team suspects that one file was changed after signing.

## Starting state

Use a host shell with the private kubeconfig for this independent kind environment. A kubeconfig identifies the cluster and credentials used by kubectl, the Kubernetes command-line tool.

```sh
export KUBECONFIG="$(astrona kubeconfig ats-031-lab-050-03-01)"
test "$(kubectl config current-context)" = "kind-astro-ats-031-lab-050-03-01" || exit 1
CONTROL=astro-ats-031-lab-050-03-01-control-plane
WORKER=astro-ats-031-lab-050-03-01-worker
```

Keep this connection selected. Host-level commands name only the node containers of this environment.

## Required result

The control plane node holds the files in `/var/lib/training-release/signed/lab`: `gpg-notes.txt` with `gpg-notes.txt.asc` and the keyring `publisher.gpg`, and `cosign-notes.txt` with `cosign-notes.txt.sig` and the key `cosign.pub`. Verify both signatures. Exactly one fails. Write the word `gpg` or `cosign`, naming the forged one, and nothing else, into `/var/lib/training-release/signed/lab/result.txt` on the control plane node. Do not change the staged files.

## Verify The Result

The grader reads the node files and the objects described above and recomputes every digest itself. Do not change the staged files.
