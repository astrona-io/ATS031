---
exam_objectives:
- Use Network security policies to restrict cluster level access
---
# Allow API Server Egress For One Pod

Under a default-deny baseline with DNS already allowed, let one pod reach the Kubernetes API server through an ipBlock /32 for the endpoint address and port, and keep every other pod away from it.

The lab runs in its own pinned kind cluster with Calico, the network plugin that enforces NetworkPolicy. The graders read the policies and send bounded live requests between pods. Python 3 is required on the grading host.

Run `astrona test` on this folder: `testing/verify-start.sh` checks that every outcome fails on the starting state, then the reference solution is applied and every outcome must pass.
