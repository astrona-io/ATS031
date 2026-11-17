---
exam_objectives:
- Use Network security policies to restrict cluster level access
---
# Allow One Peer And Deny Another

Write one ingress policy that admits one pod by its label and prove, with live requests, that this policy and nothing else blocks a pod in the same namespace and a pod in another namespace.

The lab runs in its own pinned kind cluster with Calico, the network plugin that enforces NetworkPolicy. The graders read the policies and send bounded live requests between pods. Python 3 is required on the grading host.

Run `astrona test` on this folder: `testing/verify-start.sh` checks that every outcome fails on the starting state, then the reference solution is applied and every outcome must pass.
