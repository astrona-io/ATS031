---
draft: true
exam_objectives:
- Use Network security policies to restrict cluster level access
---
# Allow One Peer And Deny Another

Enforce both an allowed same-namespace peer and a denied peer in another namespace. The task and reference solution use a separate pinned kind cluster. The grader checks declared fields and bounded live evidence. Python 3 is required on the grading host.

Run `astrona test` on this folder: `testing/verify-start.sh` checks that every outcome fails on the starting state, then the reference solution is applied and every outcome must pass.
