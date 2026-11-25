---
exam_objectives:
- Use Network security policies to restrict cluster level access
---
# Starting Environment

The namespace `starfleet-031-010-03-05` runs the pod `meter`. It listens on TCP ports 7000, 7001, 7002 and 7100, and on UDP port 7200. Its pod spec names TCP port 7100 `admin` and UDP port 7200 `tick`. The namespace `outpost-031-010-03-05` runs the pods `surveyor` and `loiterer`. Each pod has the label `app: <pod name>` and contains a small test client, `/app/client.py`. No NetworkPolicy exists.
