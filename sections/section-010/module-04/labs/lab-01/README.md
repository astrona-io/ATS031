---
draft: true
exam_objectives:
- Use Network security policies to restrict cluster level access
---
# Repair A Broken Policy Set

Repair a broken policy set until DNS, the Service call and the API call work, without opening more than needed. The grader runs the scout script, checks the effective rules and bounded denied requests. The setup reads the API server endpoint from the EndpointSlice. Python 3 is required on the grading host.

Run `astrona test` on this folder: `testing/verify-start.sh` checks that every outcome fails on the starting state, then the reference solution is applied and every outcome must pass.
