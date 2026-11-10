---
draft: true
exam_objectives:
- Properly set up Ingress with TLS
---
# Verify TLS Termination And Server Identity

Route HTTPS through the controller and verify both matching and mismatched certificate identities. The task and reference solution use a separate pinned kind cluster. The grader checks declared fields and bounded live evidence. Python 3 is required on the grading host.

Run `astrona test` on this folder: `testing/verify-start.sh` checks that every outcome fails on the starting state, then the reference solution is applied and every outcome must pass.
