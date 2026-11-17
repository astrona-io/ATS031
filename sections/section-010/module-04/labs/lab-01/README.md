---
exam_objectives:
- Use Network security policies to restrict cluster level access
---
# Repair A Broken Policy Set

Under a default-deny baseline, repair two policies: an egress policy whose DNS rule selects the wrong namespace label and misses TCP 53, and an ingress policy that was written as egress with a misspelled peer label.

The lab runs in its own pinned kind cluster with Calico, the network plugin that enforces NetworkPolicy. The graders read the policies and send bounded live requests between pods. Python 3 is required on the grading host.

Run `astrona test` on this folder: `testing/verify-start.sh` checks that every outcome fails on the starting state, then the reference solution is applied and every outcome must pass.
