---
exam_objectives:
- Use Network security policies to restrict cluster level access
---
# Record A Test Matrix For A Policy Set

Run a bounded test matrix against an existing policy set and record the observed result of every row in a ConfigMap; the grader repeats each request and compares.

The lab runs in its own pinned kind cluster with Calico, the network plugin that enforces NetworkPolicy. The graders read the policies and send bounded live requests between pods. Python 3 is required on the grading host.

Run `astrona test` on this folder: `testing/verify-start.sh` checks that every outcome fails on the starting state, then the reference solution is applied and every outcome must pass.
