---
draft: true
exam_objectives:
- Verify platform binaries before deploying
---
# Pin An Image By Digest And Prove It Runs

Solve this question on: `terminal`

The `relay` Deployment in `starfleet-031-050-03-02` runs `docker.io/library/busybox:1.36.1` from a tag, with one replica. The team wants the Deployment to run the exact image it runs now, whatever the tag points to later.

Use a host shell with the private kubeconfig for this independent kind environment. A kubeconfig identifies the cluster and credentials used by kubectl, the Kubernetes command-line tool.

```sh
export KUBECONFIG="$(astrona kubeconfig ats-031-lab-050-03-02)"
test "$(kubectl config current-context)" = "kind-astro-ats-031-lab-050-03-02" || exit 1
CONTROL=astro-ats-031-lab-050-03-02-control-plane
WORKER=astro-ats-031-lab-050-03-02-worker
```

Keep this connection selected. Host-level commands name only the node containers of this environment.

Allow about 8 minutes for task work. Cluster startup adds time.

## Tasks

1. Read the `imageID` that the running `relay` pod reports in its container status.
2. Change the image of the `relay` Deployment to a reference that ends with `@sha256:<digest>`, where the digest is the one from that `imageID`. Keep the busybox repository, and wait for the rollout.
3. Record the result in a ConfigMap named `image-pin-review` in `starfleet-031-050-03-02` with the keys `digest` (the value `sha256:<digest>`) and `imageID` (the `imageID` that the new pod reports). The new pod must report an `imageID` with the same digest.

## Constraints

- Keep the busybox repository and the `relay` Deployment name.
- Keep one replica, so exactly one `relay` pod runs after the rollout.

## How the answer is checked

The grader runs two checks. The first reads the `relay` Deployment and needs a busybox image that ends with `@sha256:` and a 64 character digest, a finished rollout with one updated and ready replica, exactly one `relay` pod, and an `imageID` on that pod that ends with the same digest. The second reads the ConfigMap `image-pin-review` and needs `imageID` equal to the `imageID` of the running `relay` pod and `digest` equal to `sha256:` followed by the digest in that `imageID`.

Hint: `kubectl -n starfleet-031-050-03-02 get pods -l app=relay -o jsonpath='{.items[0].status.containerStatuses[0].imageID}'` prints the `imageID`.
