---
exam_objectives:
- Use Network security policies to restrict cluster level access
---
# Starting Environment

The namespace `dock-031-010-02-02` runs the pods `vault` and `crane`, and the namespace `outpost-031-010-02-02` runs the pod `visitor`. Each pod has the label `app: <pod name>`, serves HTTP on TCP port 8080 and contains a small test client, `/app/client.py`. No NetworkPolicy exists.
