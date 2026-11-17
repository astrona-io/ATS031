---
exam_objectives:
- Use Network security policies to restrict cluster level access
---
# Find The Policy That Blocks A Request

Troubleshoot a namespace with a default-deny baseline: find which policy blocks an allowed request and repair it without removing the baseline or opening other paths.

The lab runs in its own pinned kind cluster with Calico, the network plugin that enforces NetworkPolicy. The graders read the policies and send bounded live requests between pods. Python 3 is required on the grading host.

Run `astrona test` on this folder: `testing/verify-start.sh` checks that every outcome fails on the starting state, then the reference solution is applied and every outcome must pass.
