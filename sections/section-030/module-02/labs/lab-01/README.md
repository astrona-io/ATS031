---
draft: true
exam_objectives:
- Properly set up Ingress with TLS
---
# Route Two Services From One Host

Publish two Services behind one host with path rules. The task and the reference solution use a separate pinned kind cluster. The grader checks declared fields and bounded live evidence from inside the cluster. Python 3 is required on the grading host.

Run `astrona test` on this folder: `testing/verify-start.sh` checks that every outcome fails on the starting state, then the reference solution is applied and every outcome must pass.
