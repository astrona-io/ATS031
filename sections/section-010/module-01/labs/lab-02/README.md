---
exam_objectives:
- Use Network security policies to restrict cluster level access
---
# Allow DNS And One Application Dependency

Isolate one pod for egress and allow exactly two dependencies: DNS to CoreDNS and TCP 8080 to the archive pods. A healthy decoy listener proves that the rest of the egress is blocked.

The lab runs in its own pinned kind cluster with Calico, the network plugin that enforces NetworkPolicy. The graders read the policies and send bounded live requests between pods. Python 3 is required on the grading host.

Run `astrona test` on this folder: `testing/verify-start.sh` checks that every outcome fails on the starting state, then the reference solution is applied and every outcome must pass.
