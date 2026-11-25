---
exam_objectives:
- Use Network security policies to restrict cluster level access
---
# Starting Environment

The namespace `starfleet-031-010-04-03` runs the pods `operator` and `helper`. The `operator` pod uses the ServiceAccount `operator`. Each pod has the label `app: <pod name>`, serves HTTP on TCP port 8080 and contains a small test client, `/app/client.py`. Two NetworkPolicies exist: `default-deny-all` isolates every pod for both directions, and `allow-dns` lets every pod reach CoreDNS on port 53.
