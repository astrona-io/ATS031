---
draft: true
exam_objectives:
- Verify platform binaries before deploying
---
# Find The Binary That Fails Verification

The control plane node holds the files in `/var/lib/training-release/k8s/lab`.

The task and solution use a separate pinned kind cluster named `ats-031-lab-050-02-01`. Run `testing/smoke.sh` with its private kubeconfig to verify initial rejection and reference success. Static validation is not live evidence. Runtime verification remains pending.
