---
exam_objectives:
- Use Network security policies to restrict cluster level access
---
# Allow A Pod Range With ipBlock And except

Write an ingress rule with an ipBlock for the cluster pod range and an except entry that removes one pod address, then prove the difference with two clients.

The lab runs in its own pinned kind cluster with Calico, the network plugin that enforces NetworkPolicy. The graders read the policies and send bounded live requests between pods. Python 3 is required on the grading host.

Run `astrona test` on this folder: `testing/verify-start.sh` checks that every outcome fails on the starting state, then the reference solution is applied and every outcome must pass.
