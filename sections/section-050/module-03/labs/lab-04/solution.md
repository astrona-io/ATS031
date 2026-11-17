---
exam_objectives:
- Verify platform binaries before deploying
---
# Pin An Image By Digest And Prove It Runs: Solution

Connect to the lab first, so that `kubectl` talks to this lab's cluster:

```sh
export KUBECONFIG="$(astrona kubeconfig ats-031-lab-050-03-04)"
```

The digest depends on the image that was loaded into your lab nodes, so your digest differs from the one below. The output comes from one run.

## Read the digest the pod runs

The `imageID` field in the pod status names the image that the container runtime started. The kubelet copies it from the runtime. Read it from the running `relay` pod:

```sh
kubectl -n starfleet-031-050-03-04 get pods -l app=relay \
  -o jsonpath='{.items[0].status.containerStatuses[0].imageID}{"\n"}'
```

```text
docker.io/library/python@sha256:673651b211bd81589d3a8688d65200b44565d6ecb0cd5bb0205b31a067f4b5e6
```

The part after `@` is the digest. Keep the value with `sha256:` in front of it.

## Pin the Deployment

`kubectl set image` changes the image of one container in the pod template. The Deployment controller then starts a new pod and stops the old one. Use the container name `relay` and your own digest:

```sh
kubectl -n starfleet-031-050-03-04 set image deployment/relay \
  relay=docker.io/library/python:3.13-alpine@sha256:673651b211bd81589d3a8688d65200b44565d6ecb0cd5bb0205b31a067f4b5e6
kubectl -n starfleet-031-050-03-04 rollout status deployment/relay --timeout=120s
```

```text
deployment.apps/relay image updated
Waiting for deployment "relay" rollout to finish: 1 old replicas are pending termination...
Waiting for deployment "relay" rollout to finish: 1 old replicas are pending termination...
deployment "relay" successfully rolled out
```

The reference keeps the tag for readers, but the container runtime resolves the image by the digest. The rollout reports success while the old pod is still stopping. Wait until only one pod is listed:

```sh
kubectl -n starfleet-031-050-03-04 get pods -l app=relay
```

```text
NAME                     READY   STATUS        RESTARTS   AGE
relay-55f7c74496-9hpzt   1/1     Terminating   0          21s
relay-56bd65f7c8-6tttx   1/1     Running       0          9s
```

This output still shows the old pod in `Terminating`. Run the command again after a few seconds until only the new pod is left. Then read its `imageID` with the same `jsonpath` command as before. It must show the same digest:

```text
docker.io/library/python@sha256:673651b211bd81589d3a8688d65200b44565d6ecb0cd5bb0205b31a067f4b5e6
```

## Record the result

Create the ConfigMap with your own values:

```sh
kubectl -n starfleet-031-050-03-04 create configmap image-pin-review \
  --from-literal=digest=sha256:673651b211bd81589d3a8688d65200b44565d6ecb0cd5bb0205b31a067f4b5e6 \
  --from-literal=imageID=docker.io/library/python@sha256:673651b211bd81589d3a8688d65200b44565d6ecb0cd5bb0205b31a067f4b5e6
```

```text
configmap/image-pin-review created
```

The grader checks that the Deployment image ends with `@sha256:` and a 64 character digest, that exactly one `relay` pod runs, that its `imageID` carries that digest, and that the ConfigMap holds that `imageID` and digest.
