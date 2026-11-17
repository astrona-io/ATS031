---
exam_objectives:
- Protect node metadata and endpoints
---
# Starting Environment

The namespace `starfleet-031-040-01-02` has the `probe` Deployment with two replicas and the `probe` Service on port 80, which forwards to port 8080 of the pods. It also has the client pod `courier` with the label `app=courier` and the pod `metadata-simulator`, a web server on port 8080 that stands in for a metadata endpoint. The namespace `outpost-031-040-01-02` has the web server pod `beacon` on port 8080 and the client pod `drifter`. No NetworkPolicy exists, so every pod can reach every other pod.
