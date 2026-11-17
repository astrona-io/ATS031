---
exam_objectives:
- Use Network security policies to restrict cluster level access
---
# Repair A Two-Entry Peer Rule

A policy lists a namespaceSelector and a podSelector as two separate peer entries, so it admits far more than intended. Repair it into one combined entry and prove the result with live requests.

The lab runs in its own pinned kind cluster with Calico, the network plugin that enforces NetworkPolicy. The graders read the policies and send bounded live requests between pods. Python 3 is required on the grading host.

Run `astrona test` on this folder: `testing/verify-start.sh` checks that every outcome fails on the starting state, then the reference solution is applied and every outcome must pass.
