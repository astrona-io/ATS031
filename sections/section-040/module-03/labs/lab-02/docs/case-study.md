---
draft: true
exam_objectives:
- Protect node metadata and endpoints
---
# Starting Environment

The cluster has one control plane node and one worker node. The kubelet on the worker serves its read-only port 10255 on purpose, and both kubelets serve HTTPS on port 10250. The namespaces `starfleet`, `outpost` and `dock` each have a `probe` Deployment and Service on port 80 and a client pod with the `curl` command. The namespace `metadata-stub` has a pod `control` that no policy selects. The pods `runtime-peek`, `cri-helper`, `log-reader` and `net-tool` expose host resources. No NetworkPolicy exists. The ConfigMap `exposed-pods` does not exist.
