---
exam_objectives:
- Use Network security policies to restrict cluster level access
---
# Starting Environment

The namespace `outpost-031-010-01-04` runs three pods: `lander`, `depot` and `stray`. Each pod has the label `app: <pod name>`, serves HTTP on TCP port 8080 and contains a small test client, `/app/client.py`. Three NetworkPolicies exist: `default-deny-all`, `lander-egress` and `depot-ingress`.
