---
exam_objectives:
- Use Network security policies to restrict cluster level access
---
# Deny All Ingress In One Namespace

Apply an ingress-only default-deny baseline to one namespace and prove that it blocks incoming requests from every source while outgoing requests keep working.

The lab runs in its own pinned kind cluster with Calico, the network plugin that enforces NetworkPolicy. The graders read the policies and send bounded live requests between pods. Python 3 is required on the grading host.

Run `astrona test` on this folder: `testing/verify-start.sh` checks that every outcome fails on the starting state, then the reference solution is applied and every outcome must pass.
