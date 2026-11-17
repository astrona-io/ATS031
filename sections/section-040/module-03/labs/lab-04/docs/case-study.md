---
exam_objectives:
- Protect node metadata and endpoints
---
# Starting Environment

The cluster has one control plane node and one worker node. The namespaces `dock-031-040-03-04` and `outpost-031-040-03-04` hold six pods. Some of them set `hostNetwork: true`, one runs a privileged container on the pod network, and the others are ordinary pods. No namespace has a Pod Security label.
