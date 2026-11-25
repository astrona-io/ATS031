---
exam_objectives:
- Properly set up Ingress with TLS
---
# Redirect HTTP To HTTPS And Add HSTS

Redirect HTTP to HTTPS on the Traefik entrypoint and add an HSTS header to one route. The task and the reference solution use a separate pinned kind cluster. The grader checks declared fields and bounded live evidence from inside the cluster. Python 3 is required on the grading host.

Run `astrona test` on this folder: `testing/verify-start.sh` checks that every outcome fails on the starting state, then the reference solution is applied and every outcome must pass.
