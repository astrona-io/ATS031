---
draft: true
exam_objectives:
- Verify platform binaries before deploying
---
# Find The Binary That Fails Verification

The control plane node holds the files in `/var/lib/training-release/k8s/lab`.

The task and solution use a separate pinned kind cluster named `ats-031-lab-050-02-01`. Run `astrona test` on this folder: `testing/verify-start.sh` checks that every outcome fails on the starting state, then the reference solution is applied and every outcome must pass.
