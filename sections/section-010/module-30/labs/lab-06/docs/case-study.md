---
exam_objectives:
- Use Network security policies to restrict cluster level access
---
# Starting Environment

The namespace `starfleet-031-010-03-06` runs the Deployment `kiosk` with two replicas, the Service `kiosk` and the pods `visitor` and `collector`. The Service listens on port 80 and sends requests to the container port named `http`, which is TCP port 8080. The `kiosk` pods also serve metrics on TCP ports 9100, 9101 and 9102. Each pod has the label `app: <name>` and contains a small test client, `/app/client.py`. Two NetworkPolicies exist: `default-deny-ingress` and `kiosk-ingress`.
