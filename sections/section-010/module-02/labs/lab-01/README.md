---
exam_objectives:
- Use Network security policies to restrict cluster level access
---
# Apply A Default-Deny Baseline And Allow One Path

Isolate every pod in one namespace for both directions, then open exactly one path that needs an egress rule on the client and an ingress rule on the server.

The lab runs in its own pinned kind cluster with Calico, the network plugin that enforces NetworkPolicy. The graders read the policies and send bounded live requests between pods. Python 3 is required on the grading host.

Run `astrona test` on this folder: `testing/verify-start.sh` checks that every outcome fails on the starting state, then the reference solution is applied and every outcome must pass.
