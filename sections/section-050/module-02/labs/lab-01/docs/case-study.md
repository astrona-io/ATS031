---
draft: true
exam_objectives:
- Verify platform binaries before deploying
---
# Starting Environment

The release team staged the three binaries `kubectl`, `kubeadm` and `kubelet` for the `starfleet` clusters. Each has a published checksum file. One of the three was changed after its checksum was published.

The environment holds a staged fixture that the bootstrap built when it started. Every digest and key in it was created at that moment.
