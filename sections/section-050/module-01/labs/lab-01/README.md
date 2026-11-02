---
draft: true
exam_objectives:
- Verify platform binaries before deploying
---
# Verify Signed Artifact Checksums

Verify a signed checksum manifest and reject altered bytes before using a binary.

The task and solution use a separate pinned kind cluster. Run `testing/smoke.sh` with its private kubeconfig to verify initial rejection and reference success. Static validation is not live evidence. Runtime verification remains pending.
