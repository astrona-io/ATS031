---
exam_objectives:
- Use Network security policies to restrict cluster level access
---
# Allow Only DNS Egress Under A Baseline

Under a default-deny baseline, give one pod DNS egress to CoreDNS on UDP and TCP port 53 and nothing else, and prove that a second pod still cannot resolve names.

The lab runs in its own pinned kind cluster with Calico, the network plugin that enforces NetworkPolicy. The graders read the policies and send bounded live requests between pods. Python 3 is required on the grading host.

Run `astrona test` on this folder: `testing/verify-start.sh` checks that every outcome fails on the starting state, then the reference solution is applied and every outcome must pass.
