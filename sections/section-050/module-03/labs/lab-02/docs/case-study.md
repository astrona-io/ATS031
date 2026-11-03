---
draft: true
exam_objectives:
- Verify platform binaries before deploying
---
# Starting Environment

The `relay` Deployment in `starfleet` runs `busybox` from a tag. The team wants the Deployment to run the exact image it runs now, whatever the tag points to later.

The environment holds a staged fixture that the bootstrap built when it started. Every digest and key in it was created at that moment.
