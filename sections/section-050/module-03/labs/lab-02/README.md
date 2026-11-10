---
draft: true
exam_objectives:
- Verify platform binaries before deploying
---
# Pin An Image By Digest And Prove It Runs

Change the image of the `relay` Deployment in the `starfleet-031-050-03-02` namespace from `docker.io/library/busybox:1.36.1` to a reference that ends with `@sha256:<digest>`, where the digest is the one the currently running pod reports in its `imageID`.

The task and solution use a separate pinned kind cluster named `ats-031-lab-050-03-02`. Run `astrona test` on this folder: `testing/verify-start.sh` checks that every outcome fails on the starting state, then the reference solution is applied and every outcome must pass.
