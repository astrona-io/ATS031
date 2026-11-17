---
draft: true
exam_objectives:
- Verify platform binaries before deploying
---
# Identify The Forged Signature

Solve this question on: `terminal`

Two release notes arrived with detached signatures, one made with GPG and one made with cosign. The Starfleet team suspects that one file was changed after signing. The control plane node holds the files in `/var/lib/training-release/signed/lab`: `gpg-notes.txt` with `gpg-notes.txt.asc` and the keyring `publisher.gpg`, and `cosign-notes.txt` with `cosign-notes.txt.sig` and the key `cosign.pub`.

Use a host shell with the private kubeconfig for this independent kind environment. A kubeconfig identifies the cluster and credentials used by kubectl, the Kubernetes command-line tool.

```sh
export KUBECONFIG="$(astrona kubeconfig ats-031-lab-050-03-01)"
test "$(kubectl config current-context)" = "kind-astro-ats-031-lab-050-03-01" || exit 1
CONTROL=astro-ats-031-lab-050-03-01-control-plane
WORKER=astro-ats-031-lab-050-03-01-worker
```

Keep this connection selected. Host-level commands name only the node containers of this environment.

Allow about 8 minutes for task work. Cluster startup adds time.

## Tasks

1. On the control plane node, verify the GPG signature `gpg-notes.txt.asc` over `gpg-notes.txt` with the keyring `publisher.gpg`.
2. Verify the cosign signature `cosign-notes.txt.sig` over `cosign-notes.txt` with the key `cosign.pub`. Exactly one of the two signatures fails.
3. Write the word `gpg` or `cosign`, naming the forged one, and nothing else, into `/var/lib/training-release/signed/lab/result.txt` on the control plane node.

## Constraints

- Do not change the staged files.

## How the answer is checked

The grader runs one check. It verifies both signatures again on the control plane node and needs `result.txt` to name the one that fails: `gpg` or `cosign`. The check also fails when the staged files were changed so that not exactly one signature fails.

Hint: cosign checks the transparency log by default. The key in this lab is local, so verify the blob with `--insecure-ignore-tlog=true`.
