---
exam_objectives:
- Use Network security policies to restrict cluster level access
---
# Allow A TCP Port Range And A Named UDP Port

Write one ingress rule that allows a TCP port range with endPort and a UDP port by its container port name, while another TCP port of the same pod stays closed.

The lab runs in its own pinned kind cluster with Calico, the network plugin that enforces NetworkPolicy. The graders read the policies and send bounded live requests between pods. Python 3 is required on the grading host.

Run `astrona test` on this folder: `testing/verify-start.sh` checks that every outcome fails on the starting state, then the reference solution is applied and every outcome must pass.
