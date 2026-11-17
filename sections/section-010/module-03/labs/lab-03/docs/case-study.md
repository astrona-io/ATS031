---
exam_objectives:
- Use Network security policies to restrict cluster level access
---
# Starting Environment

The namespace `starfleet-031-010-03-03` runs the pod `archive`. The namespaces `survey-031-010-03-03`, `salvage-031-010-03-03` and `outpost-031-010-03-03` each run a pod named `mapper`. Each pod has the label `app: <pod name>`, serves HTTP on TCP port 8080 and contains a small test client, `/app/client.py`. No NetworkPolicy exists.
