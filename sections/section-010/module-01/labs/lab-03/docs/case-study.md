---
exam_objectives:
- Use Network security policies to restrict cluster level access
---
# Starting Environment

The namespace `starfleet-031-010-01-03` runs three pods: `relay`, `lander` and `courier`. Each pod has the label `app: <pod name>`, serves HTTP on TCP port 8080 and contains a small test client, `/app/client.py`. No NetworkPolicy exists, so every pod can reach every other pod.
