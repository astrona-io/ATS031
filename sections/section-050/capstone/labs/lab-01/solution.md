---
draft: true
exam_objectives:
- Verify platform binaries before deploying
---
# Verify Before You Deploy Capstone Solution

Select the environment first:

```sh
export KUBECONFIG="$(astrona kubeconfig ats-031-capstone-050)"
test "$(kubectl config current-context)" = "kind-astro-ats-031-capstone-050" || exit 1
CONTROL=astro-ats-031-capstone-050-control-plane
WORKER=astro-ats-031-capstone-050-worker
B=/var/lib/training-release/bundle
```

Verify the manifest signature. The command exits with status 0 and prints a verification message only if the signature matches:

```sh
podman exec $CONTROL sh -c "cd $B && openssl dgst -sha256 -verify publisher.pub -signature SHA256SUMS.sig SHA256SUMS"
```

Check each binary against its manifest line. A line that passes is followed by `OK`, and one that fails prints `FAILED`:

```sh
podman exec $CONTROL sh -c "cd $B && grep ' kubectl\$' SHA256SUMS | sha256sum --check"
podman exec $CONTROL sh -c "cd $B && grep ' kubeadm\$' SHA256SUMS | sha256sum --check"
```

Copy the one binary that passes, replacing `<tool>`:

```sh
podman exec $CONTROL cp $B/<tool> /var/lib/training-release/approved/<tool>
```

Check the running kubelet on the worker node and compare the digest with the `kubelet` line of the manifest:

```sh
KUBELET_PID=$(podman exec $WORKER sh -c "grep -l '^kubelet\$' /proc/[0-9]*/comm | head -n 1 | cut -d/ -f3")
podman exec $WORKER sha256sum /proc/$KUBELET_PID/exe
podman exec $CONTROL grep ' kubelet\$' $B/SHA256SUMS
```

Read the `imageID` of the running pod and pin the Deployment. Replace `<digest>` with the 64 characters after `sha256:`:

```sh
kubectl -n starfleet get pods -l app=relay -o jsonpath='{.items[0].status.containerStatuses[0].imageID}{"\n"}'
kubectl -n starfleet set image deployment/relay relay=docker.io/library/busybox:1.37.0@sha256:<digest>
kubectl -n starfleet rollout status deployment/relay
```

Record the report. Save this as `configmap-verification-report.yaml`, with your own values:

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: verification-report
  namespace: starfleet
data:
  manifest_signature: verified
  genuine: <name>
  rejected: <name>
  kubelet: <match-or-mismatch>
  kubelet_sha256: <digest>
  image: docker.io/library/busybox:1.37.0@sha256:<digest>
```

```sh
kubectl apply -f configmap-verification-report.yaml
```

After you finish, remove the independent environment with `astrona destroy ats-031-capstone-050`.

## Common pitfalls

> [!WARNING]
> Verify the signature of the manifest before you use any digest from it. A passing digest in an unsigned manifest proves nothing about the publisher. Do not copy a binary to the approved directory before it passes, and do not leave a rejected one there.
