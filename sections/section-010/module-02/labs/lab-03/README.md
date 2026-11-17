---
exam_objectives:
- Use Network security policies to restrict cluster level access
---
# Deny All Egress And Observe DNS Fail

Apply an egress-only default-deny baseline to one namespace, observe that DNS stops along with every outgoing request, and keep incoming requests open.

The lab runs in its own pinned kind cluster with Calico, the network plugin that enforces NetworkPolicy. The graders read the policies and send bounded live requests between pods. Python 3 is required on the grading host.

Run `astrona test` on this folder: `testing/verify-start.sh` checks that every outcome fails on the starting state, then the reference solution is applied and every outcome must pass.
