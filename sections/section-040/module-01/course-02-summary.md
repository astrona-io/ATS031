---
draft: true
exam_objectives:
- Protect node metadata and endpoints
---
# Summary

Node-local endpoints can expose authority that exceeds a workload's intended identity. Metadata, kubelet, runtime and management interfaces have different audiences and controls.

Protection combines restricted reachability, authenticated and authorized access, and narrow underlying credentials. A namespaced traffic policy is useful only where its implementation covers the actual path; cloud metadata mechanisms and host networking require their own assessment.

Node endpoint protection must account for authority outside Kubernetes API role grants.
