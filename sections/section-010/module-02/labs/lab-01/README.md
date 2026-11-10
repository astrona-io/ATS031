---
draft: true
exam_objectives:
- Use Network security policies to restrict cluster level access
---
# Apply A Default-Deny Baseline And Allow One Path

Apply a combined default-deny baseline to one namespace and open one path. The task and reference result use a separate pinned kind cluster. The grader checks declared fields, the effective rules and bounded live requests. Python 3 is required on the grading host.

Run `astrona test` on this folder: `testing/verify-start.sh` checks that every outcome fails on the starting state, then the reference solution is applied and every outcome must pass.
