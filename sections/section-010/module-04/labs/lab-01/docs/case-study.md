---
exam_objectives:
- Use Network security policies to restrict cluster level access
---
# Starting Environment

The namespace `starfleet-031-010-04-01` runs the pods `pathfinder`, `datastore` and `stranger`. The `pathfinder` pod uses the ServiceAccount `pathfinder`. Each pod has the label `app: <pod name>` and contains a small test client, `/app/client.py`. The `datastore` pod listens on TCP port 6379, and the other two pods serve HTTP on TCP port 8080.

Three NetworkPolicies exist. `default-deny-all` isolates every pod for both directions and is correct. `pathfinder-egress` is meant to let `pathfinder` use DNS, the `datastore` and the Kubernetes API server. `datastore-ingress` is meant to let only `pathfinder` connect to the `datastore`.
