---
exam_objectives:
- Use Network security policies to restrict cluster level access
---
# Starting Environment

The namespace `starfleet-031-010-04-04` runs the pods `rover`, `tanker`, `hangar` and `vault`, and the namespace `outpost-031-010-04-04` runs the pod `drone`. Each pod has the label `app: <pod name>`, serves HTTP on TCP port 8080 and contains a small test client, `/app/client.py`. Three NetworkPolicies exist in `starfleet-031-010-04-04`: `default-deny-all`, `hangar-ingress` and `rover-egress`. There is no policy in `outpost-031-010-04-04`.
