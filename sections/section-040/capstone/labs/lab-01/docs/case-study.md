---
draft: true
exam_objectives:
- Protect node metadata and endpoints
---
# Starting Environment

The cluster has the namespaces `starfleet`, `outpost` and `dock`, each with a `probe` Deployment and Service on port 80 and a client pod with the `curl` command: `shuttle` and `agent` in `starfleet`, `drifter` in `outpost` and `tender` in `dock`. The pod `agent` has the label `role=cloud-agent`. The kubelet on the worker node serves the read-only port 10255 on purpose. The namespace `metadata-stub` has `fake-imds`, a fake metadata server on the worker at `169.254.169.254` port 80, and the pod `control` that no policy selects. The Deployment `runtime-peek` in `outpost` mounts the container runtime socket. No NetworkPolicy exists.
