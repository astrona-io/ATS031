---
draft: true
exam_objectives:
- Use Network security policies to restrict cluster level access
---
# Repair A Broken Policy Set

Repair a broken policy set until DNS, the Service call and the API call work, without opening more than needed. The grader runs the scout script, checks the effective rules and bounded denied requests. The setup reads the API server endpoint from the EndpointSlice. Python 3 is required on the grading host.

Run `testing/smoke.sh` with the lab's private kubeconfig to prove that the starting state fails and the reference result passes. Each wait and request is bounded. Live verification is pending until a real container-engine run is recorded. Static checks are not runtime evidence.
