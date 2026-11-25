---
exam_objectives:
- Use Network security policies to restrict cluster level access
---
# Starting Environment

The namespace `outpost-031-010-02-01` runs the pods `forge`, `smith` and `idler`, and the namespace `dock-031-010-02-01` runs the pod `visitor`. Each pod has the label `app: <pod name>`, serves HTTP on TCP port 8080 and contains a small test client, `/app/client.py`. No NetworkPolicy exists, so every pod can reach every other pod.
