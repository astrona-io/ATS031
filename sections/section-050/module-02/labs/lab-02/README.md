---
draft: true
exam_objectives:
- Verify platform binaries before deploying
---
# Verify The Running kubelet Against A Release Checksum

On the worker node, find the running `kubelet` process, resolve the binary it runs through `/proc/<pid>/exe`, read its version, and compare the digest of that binary with the staged release checksum for that version.

The task and solution use a separate pinned kind cluster named `ats-031-lab-050-02-02`. Run `testing/smoke.sh` with its private kubeconfig to verify initial rejection and reference success. Static validation is not live evidence. Runtime verification remains pending.
