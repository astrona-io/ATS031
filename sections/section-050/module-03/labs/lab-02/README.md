---
draft: true
exam_objectives:
- Verify platform binaries before deploying
---
# Pin An Image By Digest And Prove It Runs

Change the image of the `relay` Deployment in the `starfleet` namespace from `docker.io/library/busybox:1.37.0` to a reference that ends with `@sha256:<digest>`, where the digest is the one the currently running pod reports in its `imageID`.

The task and solution use a separate pinned kind cluster named `ats-031-lab-050-03-02`. Run `testing/smoke.sh` with its private kubeconfig to verify initial rejection and reference success. Static validation is not live evidence. Runtime verification remains pending.
