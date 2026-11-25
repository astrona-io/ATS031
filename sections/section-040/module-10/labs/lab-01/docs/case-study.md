---
exam_objectives:
- Protect node metadata and endpoints
---
# Starting Environment

The namespace `starfleet-031-040-01-01` has the `probe` Deployment and Service, the pod `metadata-simulator` (a web server on port 8080 that stands in for a metadata endpoint) and the Deployment `relay` with one client pod. The NetworkPolicy `starfleet-egress` selects every pod in the namespace and allows egress only to the cluster DNS pods and to the `probe` pods on port 8080. The pod template of `relay` sets `hostNetwork: true`. The namespace `outpost-031-040-01-01` has the client pod `drifter` and no NetworkPolicy.
