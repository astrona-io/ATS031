---
exam_objectives:
- Use Network security policies to restrict cluster level access
---
# Apply One Baseline To Labelled Namespaces

Mark two namespaces with a label and apply the same default-deny baseline file to every namespace that carries the label, while a third namespace stays open.

The lab runs in its own pinned kind cluster with Calico, the network plugin that enforces NetworkPolicy. The graders read the policies and send bounded live requests between pods. Python 3 is required on the grading host.

Run `astrona test` on this folder: `testing/verify-start.sh` checks that every outcome fails on the starting state, then the reference solution is applied and every outcome must pass.
