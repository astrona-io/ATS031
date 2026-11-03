---
draft: true
exam_objectives:
- Use Network security policies to restrict cluster level access
---
# Secure Three Namespaces With Network Policies

Capstone for network policy: baselines in three namespaces, a repaired cross-namespace rule, DNS, an external range and an API server rule. The grader checks declared fields, the effective rules and bounded live requests. Python 3 is required on the grading host.

Run `testing/smoke.sh` with the lab's private kubeconfig to prove that the starting state fails and the reference result passes. Each wait and request is bounded. Live verification is pending until a real container-engine run is recorded. Static checks are not runtime evidence.
