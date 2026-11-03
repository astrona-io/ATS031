---
draft: true
exam_objectives:
- Verify platform binaries before deploying
---
# Pin An Image By Digest And Prove It Runs

The `relay` Deployment in `starfleet` runs `busybox` from a tag. The team wants the Deployment to run the exact image it runs now, whatever the tag points to later.

## Starting state

Use a host shell with the private kubeconfig for this independent kind environment. A kubeconfig identifies the cluster and credentials used by kubectl, the Kubernetes command-line tool.

```sh
export KUBECONFIG="$(astrona kubeconfig ats-031-lab-050-03-02)"
test "$(kubectl config current-context)" = "kind-astro-ats-031-lab-050-03-02" || exit 1
CONTROL=astro-ats-031-lab-050-03-02-control-plane
WORKER=astro-ats-031-lab-050-03-02-worker
```

Keep this connection selected. Host-level commands name only the node containers of this environment.

## Required result

Change the image of the `relay` Deployment in the `starfleet` namespace from `docker.io/library/busybox:1.37.0` to a reference that ends with `@sha256:<digest>`, where the digest is the one the currently running pod reports in its `imageID`. Keep the busybox repository. Wait for the rollout. Then record the result in a ConfigMap named `image-pin-review` in `starfleet` with the keys `digest` (the value `sha256:<digest>`) and `imageID` (the `imageID` that the new pod reports). The new pod must report an `imageID` with the same digest.

## Verify The Result

The grader reads the node files and the objects described above and recomputes every digest itself. Do not change the staged files.
