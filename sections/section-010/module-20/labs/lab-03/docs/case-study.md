---
exam_objectives:
- Use Network security policies to restrict cluster level access
---
# Starting Environment

The namespace `dock-031-010-02-03` runs the pods `hauler` and `winch`, and the namespace `outpost-031-010-02-03` runs the pod `pilot`. Each pod has the label `app: <pod name>`, serves HTTP on TCP port 8080 and contains a small test client, `/app/client.py`. No NetworkPolicy exists.
