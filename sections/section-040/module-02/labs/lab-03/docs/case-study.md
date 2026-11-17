---
exam_objectives:
- Protect node metadata and endpoints
---
# Starting Environment

The cluster has the namespaces `starfleet-031-040-02-03`, `outpost-031-040-02-03` and `dock-031-040-02-03`. Each has a `probe` Deployment and Service on port 80, a client pod with the `curl` command (`shuttle`, `drifter` and `tender`), and an egress NetworkPolicy called `metadata-guard`. The namespace `metadata-stub-031-040-02-03` has the pod `fake-imds`, a fake metadata server on the host network of the worker node at `169.254.169.254` port 80, and a pod `control` that no policy selects.

The three `metadata-guard` policies each contain a different mistake. In two namespaces the client pod still reaches the metadata address. In the third namespace the client pod cannot reach the address, but it cannot reach the `probe` Service either.
