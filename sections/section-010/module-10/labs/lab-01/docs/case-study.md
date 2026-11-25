---
exam_objectives:
- Use Network security policies to restrict cluster level access
---
# Starting Environment

The namespace `starfleet-031-010-01-01` runs the Deployment `hub` with two replicas and the Service `hub`, plus the pods `tender`, `idler` and `mirror`. The Service listens on port 80 and sends requests to the container port named `http`, which is TCP port 8080. The namespace `outpost-031-010-01-01` runs the pod `stranger`. Each pod has the label `app: <name>`, serves HTTP on TCP port 8080 and contains a small test client, `/app/client.py`. No NetworkPolicy exists.
