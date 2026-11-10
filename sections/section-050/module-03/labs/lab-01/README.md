---
draft: true
exam_objectives:
- Verify platform binaries before deploying
---
# Identify The Forged Signature

The control plane node holds the files in `/var/lib/training-release/signed/lab`: `gpg-notes.txt` with `gpg-notes.txt.asc` and the keyring `publisher.gpg`, and `cosign-notes.txt` with `cosign-notes.txt.sig` and the key `cosign.pub`.

The task and solution use a separate pinned kind cluster named `ats-031-lab-050-03-01`. Run `astrona test` on this folder: `testing/verify-start.sh` checks that every outcome fails on the starting state, then the reference solution is applied and every outcome must pass.
