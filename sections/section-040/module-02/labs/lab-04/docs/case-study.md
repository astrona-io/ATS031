---
exam_objectives:
- Protect node metadata and endpoints
---
# Starting Environment

The cluster has the namespaces `starfleet-031-040-02-04`, `outpost-031-040-02-04` and `dock-031-040-02-04`, each with a `probe` Deployment and Service on port 80 and a client pod with the `curl` command. The pods `shuttle` and `agent` run in `starfleet-031-040-02-04`, and `agent` has the label `role=cloud-agent`. The pod `drifter` runs in `outpost-031-040-02-04` and the pod `tender` in `dock-031-040-02-04`. The namespace `metadata-stub-031-040-02-04` has the pod `fake-imds`, a fake metadata server on the host network of the worker node at `169.254.169.254` port 80, and a pod `control` that no policy selects.

A NetworkPolicy called `block-metadata` exists in `starfleet-031-040-02-04` and in `outpost-031-040-02-04`. The namespace `dock-031-040-02-04` has no NetworkPolicy.
