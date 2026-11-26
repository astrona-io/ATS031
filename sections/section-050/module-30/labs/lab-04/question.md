# Pin An Image By Digest And Prove It Runs

The `relay` Deployment in namespace `starfleet-031-050-03-04` runs the image `docker.io/library/python:3.13-alpine` by tag. The team wants the Deployment to keep running the exact image it runs now, even if the tag later points to another image. The kubelet reports the digest of the image that the container runtime started in the `imageID` field of the pod status.

1. Change the image of the `relay` container to `docker.io/library/python:3.13-alpine@sha256:<digest>`, with the digest from the `imageID` of the `relay` pod that runs now.
2. Wait until the rollout is complete and exactly one `relay` pod runs, and that pod reports an `imageID` with the same digest.
3. Create the ConfigMap `image-pin-review` in the same namespace with the key `digest`, set to `sha256:<digest>`, and the key `imageID`, set to the full `imageID` that the new pod reports.

Keep the `python` repository and the Deployment name; the cluster has no network access, so only the digest of the preloaded image can start.
