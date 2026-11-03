---
draft: true
exam_objectives:
- Verify platform binaries before deploying
---
# Starting Environment

Two release notes arrived with detached signatures, one made with GPG and one made with cosign. The `starfleet` team suspects that one file was changed after signing.

The environment holds a staged fixture that the bootstrap built when it started. Every digest and key in it was created at that moment.
