---
exam_objectives:
- Use Network security policies to restrict cluster level access
---
# Allow One Pod From Another Namespace

Admit one pod from one other namespace by combining a namespaceSelector and a podSelector in one peer entry. Pods with the same label in other namespaces, including the target namespace itself, must stay blocked.

The lab runs in its own pinned kind cluster with Calico, the network plugin that enforces NetworkPolicy. The graders read the policies and send bounded live requests between pods. Python 3 is required on the grading host.

Run `astrona test` on this folder: `testing/verify-start.sh` checks that every outcome fails on the starting state, then the reference solution is applied and every outcome must pass.
