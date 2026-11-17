---
exam_objectives:
- Use Network security policies to restrict cluster level access
---
# Starting Environment

The namespace `starfleet-031-010-03-01` runs the pods `registry` and `courier`. The namespace `outpost-031-010-03-01` runs the pods `courier` and `idler`, and the namespace `dock-031-010-03-01` runs one more pod named `courier`. Each pod has the label `app: <pod name>`, so three pods carry `app: courier`. Each pod serves HTTP on TCP port 8080 and contains a small test client, `/app/client.py`. Each namespace has the automatic label `kubernetes.io/metadata.name: <namespace name>`. No NetworkPolicy exists.
