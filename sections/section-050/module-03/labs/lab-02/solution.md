---
draft: true
exam_objectives:
- Verify platform binaries before deploying
---
# Pin An Image By Digest And Prove It Runs Solution

This walkthrough solves the task step by step. Run the first block to select the environment:

```sh
export KUBECONFIG="$(astrona kubeconfig ats-031-lab-050-03-02)"
test "$(kubectl config current-context)" = "kind-astro-ats-031-lab-050-03-02" || exit 1
CONTROL=astro-ats-031-lab-050-03-02-control-plane
WORKER=astro-ats-031-lab-050-03-02-worker
```

Read the `imageID` of the running pod. The text after `@sha256:` is the digest to use:

```sh
kubectl -n starfleet get pods -l app=relay -o jsonpath='{.items[0].status.containerStatuses[0].imageID}{"\n"}'
```

If the value has the form `docker.io/library/busybox@sha256:<digest>`, copy the digest. If it shows only `sha256:` followed by a value, the runtime does not report a registry digest for this image and a pin cannot be built from it; in that case read the digest column of `crictl images --digests` on the node that runs the pod.

Pin the Deployment to the digest. Replace `<digest>` with the 64 characters:

```sh
kubectl -n starfleet set image deployment/relay relay=docker.io/library/busybox:1.37.0@sha256:<digest>
kubectl -n starfleet rollout status deployment/relay
```

Read the `imageID` of the new pod and compare its digest with the one you pinned:

```sh
kubectl -n starfleet get pods -l app=relay -o jsonpath='{.items[0].status.containerStatuses[0].imageID}{"\n"}'
```

Record the review. Save this as `configmap-image-pin-review.yaml`, with your own values:

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: image-pin-review
  namespace: starfleet
data:
  digest: sha256:<digest>
  imageID: <imageID>
```

Apply it:

```sh
kubectl apply -f configmap-image-pin-review.yaml
```

After recording your result, remove the independent lab with `astrona destroy ats-031-lab-050-03-02`.

## Common pitfalls

> [!WARNING]
> Wait for the old pod to finish terminating before you read the `imageID`; the grader expects exactly one `relay` pod. A tag that stays in the field does not pin anything without the digest. Copy the digest, not the image identifier, if the two differ.
