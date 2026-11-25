---
exam_objectives:
- Use Network security policies to restrict cluster level access
---
# Starting Environment

The namespace `starfleet-031-010-03-04` runs the pod `ledger`, which serves HTTP on TCP port 7070. The namespace `outpost-031-010-03-04` runs the pods `courier` and `rogue`, which serve HTTP on TCP port 8080. Each pod has the label `app: <pod name>` and contains a small test client, `/app/client.py`. No NetworkPolicy exists. The cluster gives pod addresses from the range `192.168.0.0/16`.
