---
draft: true
exam_objectives:
- Use Network security policies to restrict cluster level access
---
# Allow One Pod From Another Namespace

Write one cross-namespace ingress policy with a combined peer entry. The grader checks the declared fields and bounded live requests. Python 3 is required on the grading host.

Run `testing/smoke.sh` with the lab's private kubeconfig to prove that the starting state fails and the reference result passes. Each wait and request is bounded. Live verification is pending until a real container-engine run is recorded. Static checks are not runtime evidence.
