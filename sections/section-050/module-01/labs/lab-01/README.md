---
draft: true
exam_objectives:
- Verify platform binaries before deploying
---
# Verify Signed Artifact Checksums

Verify a signed checksum manifest and reject altered bytes before using a binary.

The task and solution use a separate pinned kind cluster. Run `astrona test` on this folder: `testing/verify-start.sh` checks that every outcome fails on the starting state, then the reference solution is applied and every outcome must pass.
