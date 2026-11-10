---
draft: true
exam_objectives:
- Protect node metadata and endpoints
---
# Starting Environment

The cluster has the namespaces `starfleet-031-040-02-01`, `outpost-031-040-02-01` and `dock-031-040-02-01`, each with a `probe` Deployment and Service on port 80 and a client pod with the `curl` command. The pod `agent` in `starfleet-031-040-02-01` has the label `role=cloud-agent`. The namespace `metadata-stub-031-040-02-01` has the pod `fake-imds`, a fake metadata server on the host network of the worker node at `169.254.169.254` port 80, and a pod `control` that no policy selects. No NetworkPolicy exists. The required policy for `outpost-031-040-02-01` is not in place.
