---
draft: true
exam_objectives:
- Verify platform binaries before deploying
---
# Verify The Running kubelet Against A Release Checksum Solution

This walkthrough solves the task step by step. Run the first block to select the environment:

```sh
export KUBECONFIG="$(astrona kubeconfig ats-031-lab-050-02-02)"
test "$(kubectl config current-context)" = "kind-astro-ats-031-lab-050-02-02" || exit 1
CONTROL=astro-ats-031-lab-050-02-02-control-plane
WORKER=astro-ats-031-lab-050-02-02-worker
```

Find the process identifier of the `kubelet` on the worker node and resolve its binary:

```sh
KUBELET_PID=$(podman exec $WORKER sh -c "grep -l '^kubelet\$' /proc/[0-9]*/comm | head -n 1 | cut -d/ -f3")
podman exec $WORKER readlink /proc/$KUBELET_PID/exe
podman exec $WORKER kubelet --version
```

Compute the digest of the running binary and list the staged checksum files. There is one directory for each version, so use the one that matches the version the kubelet reported:

```sh
podman exec $WORKER sha256sum /proc/$KUBELET_PID/exe
podman exec $WORKER sh -c 'ls /var/lib/training-release/k8s/release/*/bin/linux/*/ && cat /var/lib/training-release/k8s/release/*/bin/linux/*/kubelet.sha256'
```

Compare the digest with the checksum file under the directory for your version. The line below checks it, and the output ends with `OK` when it matches. Replace `<version>` with the reported version, for example `v1.35.0`:

```sh
podman exec $WORKER sh -c "echo \"\$(cat /var/lib/training-release/k8s/release/<version>/bin/linux/*/kubelet.sha256)  /proc/$KUBELET_PID/exe\" | sha256sum --check"
```

Save the result as a ConfigMap. Save this as `configmap-kubelet-review.yaml`, with your own values:

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: kubelet-review
  namespace: starfleet
data:
  version: <version>
  path: <path>
  sha256: <digest>
  result: <match-or-mismatch>
```

Apply it:

```sh
kubectl apply -f configmap-kubelet-review.yaml
```

Then check the result:

```sh
kubectl -n starfleet get configmap kubelet-review -o yaml
```

After recording your result, remove the independent lab with `astrona destroy ats-031-lab-050-02-02`.

## Common pitfalls

> [!WARNING]
> The checksum of another version gives `mismatch` for a genuine kubelet, so choose the file by the reported version. Hash `/proc/<pid>/exe` or the resolved path; do not guess a path. Keep the digest exactly as printed, in lower case.
