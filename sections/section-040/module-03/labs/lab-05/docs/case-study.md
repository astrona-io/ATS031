---
exam_objectives:
- Protect node metadata and endpoints
---
# Starting Environment

The cluster has one control plane node and one worker node. The kube-apiserver static pod runs without the `NodeRestriction` admission plugin, so the worker kubelet's credential may change any Node object. The worker node carries the label `node-restriction.kubernetes.io/dedicated=payments`, which its own kubelet credential set. The namespace `starfleet-031-040-03-05` exists and is empty.
