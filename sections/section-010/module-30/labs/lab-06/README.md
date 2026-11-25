---
exam_objectives:
- Use Network security policies to restrict cluster level access
---
# Repair A Policy That Names The Service Port And Add A Port Range

Repair an ingress rule that names the Service port instead of the pod port, then add a second rule with an endPort range for a metrics client, and test every replica.

The lab runs in its own pinned kind cluster with Calico, the network plugin that enforces NetworkPolicy. The graders read the policies and send bounded live requests between pods. Python 3 is required on the grading host.

Run `astrona test` on this folder: `testing/verify-start.sh` checks that every outcome fails on the starting state, then the reference solution is applied and every outcome must pass.
