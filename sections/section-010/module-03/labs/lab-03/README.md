---
exam_objectives:
- Use Network security policies to restrict cluster level access
---
# Admit A Group Of Namespaces By Label

Label two namespaces as members of a group and write an ingress rule that admits the group with a namespaceSelector, while a namespace outside the group stays blocked.

The lab runs in its own pinned kind cluster with Calico, the network plugin that enforces NetworkPolicy. The graders read the policies and send bounded live requests between pods. Python 3 is required on the grading host.

Run `astrona test` on this folder: `testing/verify-start.sh` checks that every outcome fails on the starting state, then the reference solution is applied and every outcome must pass.
