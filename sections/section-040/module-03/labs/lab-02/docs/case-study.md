---
draft: true
exam_objectives:
- Protect node metadata and endpoints
---
# Starting Environment

The cluster has one control plane node and one worker node. The kubelet on the worker serves its read-only port 10255 on purpose, and both kubelets serve HTTPS on port 10250. The namespaces `starfleet-031-040-03-02`, `outpost-031-040-03-02` and `dock-031-040-03-02` each have a `probe` Deployment and Service on port 80 and a client pod with the `curl` command. The namespace `metadata-stub-031-040-03-02` has a pod `control` that no policy selects. The pods `runtime-peek`, `cri-helper`, `log-reader` and `net-tool` expose host resources. No NetworkPolicy exists. The ConfigMap `exposed-pods` does not exist.
