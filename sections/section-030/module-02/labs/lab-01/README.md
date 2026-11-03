---
draft: true
exam_objectives:
- Properly set up Ingress with TLS
---
# Route Two Services From One Host

Publish two Services behind one host with path rules. The task and the reference solution use a separate pinned kind cluster. The grader checks declared fields and bounded live evidence from inside the cluster. Python 3 is required on the grading host.

Run `testing/smoke.sh` with the lab's private kubeconfig to prove that the starting state fails and the reference solution passes. Live verification is pending until actual container-engine execution is recorded. Static checks are not runtime evidence.
