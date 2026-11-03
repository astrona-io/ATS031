---
draft: true
exam_objectives:
- Protect node metadata and endpoints
---
# Starting Environment

The cluster has the namespaces `starfleet`, `outpost` and `dock`, each with a `probe` Deployment and Service on port 80 and a client pod with the `curl` command. The pod `agent` in `starfleet` has the label `role=cloud-agent`. The namespace `metadata-stub` has the pod `fake-imds`, a fake metadata server on the host network of the worker node at `169.254.169.254` port 80, and a pod `control` that no policy selects. No NetworkPolicy exists. The two pods in `starfleet` differ only by the label `role=cloud-agent`.
