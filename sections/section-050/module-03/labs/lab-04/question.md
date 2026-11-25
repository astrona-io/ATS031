---
exam_objectives:
- Verify platform binaries before deploying
---
# Pin An Image By Digest And Prove It Runs

Allow about 8 minutes for the tasks.

The `relay` Deployment in `starfleet-031-050-03-04` runs the image `docker.io/library/python:3.13-alpine` by tag. The team wants the Deployment to keep running the exact image it runs now, even if the tag later points to another image.

## Connect to the lab

Use a shell on your own machine. The kubeconfig file holds the address and the credentials of this lab's cluster, and `kubectl` uses it.

```sh
export KUBECONFIG="$(astrona kubeconfig ats-031-lab-050-03-04)"
test "$(kubectl config current-context)" = "kind-astro-ats-031-lab-050-03-04" || exit 1
```

## Tasks

1. Read the `imageID` that the running `relay` pod reports. The kubelet fills this field with the digest of the image that the container runtime started.
2. Change the image of the `relay` container to `docker.io/library/python:3.13-alpine@sha256:<digest>`, with the digest from step 1. Keep the `python` repository.
3. Wait until the rollout is complete and exactly one `relay` pod runs. The new pod must report an `imageID` with the same digest.
4. Create the ConfigMap `image-pin-review` in `starfleet-031-050-03-04` with two keys: `digest`, the value `sha256:<digest>`, and `imageID`, the full `imageID` that the new pod reports.
