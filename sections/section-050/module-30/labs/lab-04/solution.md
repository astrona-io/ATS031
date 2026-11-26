# Pin An Image By Digest And Prove It Runs — Solution

You solve this lab with one image change on the Deployment and one ConfigMap. Keep `astrona submit --watch` running in a second terminal: it grades the lab again and again while you work and records nothing. Each check below turns green as you finish its task.

## Step 1: look at the starting state

Print the image in the Deployment and the `imageID` of the running pod:

```sh
kubectl -n starfleet-031-050-03-04 get deployment relay -o jsonpath='{.spec.template.spec.containers[0].image}{"\n"}'
kubectl -n starfleet-031-050-03-04 get pods -l app=relay -o jsonpath='{.items[0].status.containerStatuses[0].imageID}{"\n"}'
```

The first line is the tag `docker.io/library/python:3.13-alpine`. A tag is a name that the registry can move to another image at any time. The second line has the form `docker.io/library/python@sha256:<digest>`. The digest is the SHA-256 of the image manifest, so it names exactly one image and can never point to another.

## Step 2: pin the Deployment (check `deployment-pinned`)

Copy the 64 hex characters after `sha256:` from Step 1 and replace `<DIGEST>`. `kubectl set image` changes the image of the container `relay` in the pod template:

```sh
kubectl -n starfleet-031-050-03-04 set image deployment/relay relay=docker.io/library/python:3.13-alpine@sha256:<DIGEST>
```

The reference keeps the tag for readers, but when a reference has a digest, the runtime uses only the digest. Any change to the pod template starts a new rollout.

## Step 3: wait for the pinned pod (check `pod-pinned`)

Wait until the rollout is done:

```sh
kubectl -n starfleet-031-050-03-04 rollout status deployment/relay --timeout=180s
kubectl -n starfleet-031-050-03-04 get pods -l app=relay
```

`rollout status` ends with `deployment "relay" successfully rolled out`. If `get pods` still shows the old pod as `Terminating`, run it again until one pod is left. Then print the `imageID` of the new pod:

```sh
kubectl -n starfleet-031-050-03-04 get pods -l app=relay -o jsonpath='{.items[0].status.containerStatuses[0].imageID}{"\n"}'
```

It ends with the same `sha256:<DIGEST>` as in Step 1. This proves that the Deployment now starts the image that ran before.

## Step 4: record the result (check `pin-review`)

Replace `<DIGEST>` with the digest and `<IMAGE_ID>` with the full line from Step 3. Save this as `configmap-image-pin-review.yaml`:

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: image-pin-review
  namespace: starfleet-031-050-03-04
data:
  digest: "sha256:<DIGEST>"
  imageID: "<IMAGE_ID>"
```

Apply it:

```sh
kubectl apply -f configmap-image-pin-review.yaml
```

## Step 5: test the record

Print both keys:

```sh
kubectl -n starfleet-031-050-03-04 get configmap image-pin-review -o jsonpath='{.data.digest}{"\n"}{.data.imageID}{"\n"}'
```

The first line must show `sha256:` and the digest. The second line must be identical to the `imageID` from Step 3, and it must end with the first line.

## Step 6: submit

When `astrona submit --watch` shows every check passing, stop it and run `astrona submit`. This grades the lab for real, ends the attempt and removes the lab.

## Common pitfalls

> [!WARNING]
> Do not take the digest from anywhere other than the running pod or the node. The grader requires the digest of the image that `relay` ran at the start.
>
> Do not change the repository. The image must be `docker.io/library/python:3.13-alpine@sha256:<digest>`, or `python:3.13-alpine@sha256:<digest>` for short.
>
> Do not record the ConfigMap before the rollout is done. While the old pod still exists, the grader finds more than one `relay` pod and fails the pod checks.
>
> Record `digest` with the `sha256:` prefix, and `imageID` as the full value, with the `docker.io/library/python@` part.
