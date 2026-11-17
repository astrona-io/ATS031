---
draft: true
exam_objectives:
- Verify platform binaries before deploying
---
# Verify Before You Deploy Capstone

Solve this question on: `terminal`

The `starfleet` team received a release bundle for the cluster nodes. The bundle holds two binaries, `kubectl` and `kubeadm`, a manifest of digests named `SHA256SUMS`, a signature `SHA256SUMS.sig` over the manifest, the publisher public key `publisher.pub` and an image reference in `image.txt`. The manifest also lists the digest of the `kubelet` that the worker node must run. The bundle files are on the control plane node in `/var/lib/training-release/bundle`. One of the two binaries was changed after the manifest was signed. The Deployment `relay` in `starfleet` runs `docker.io/library/busybox:1.37.0` by tag.

Use a host shell with the private kubeconfig for this independent kind environment. A kubeconfig identifies the cluster and credentials used by kubectl, the Kubernetes command-line tool.

```sh
export KUBECONFIG="$(astrona kubeconfig ats-031-capstone-050)"
test "$(kubectl config current-context)" = "kind-astro-ats-031-capstone-050" || exit 1
CONTROL=astro-ats-031-capstone-050-control-plane
WORKER=astro-ats-031-capstone-050-worker
```

Keep this connection selected. Host-level commands name only the node containers of this environment.

Allow about 25 minutes for task work. Cluster startup adds time.

## Tasks

1. Verify the signature of `SHA256SUMS` with `publisher.pub`. Do this before you trust any digest in the manifest.
2. Check `kubectl` and `kubeadm` against the manifest. Copy only the binaries that pass into `/var/lib/training-release/approved` on the control plane node. That directory must hold nothing else.
3. Resolve the binary of the running `kubelet` on the worker node through `/proc/<pid>/exe` and compare its digest with the `kubelet` line of the manifest.
4. Pin the `relay` Deployment to the digest of the image that its pod runs now. Keep the busybox repository in the reference. Wait for the rollout.
5. Record the result in a ConfigMap named `verification-report` in `starfleet` with these keys: `manifest_signature` (`verified`), `genuine` (the approved binary names, comma-joined and sorted), `rejected` (the rejected binary names, comma-joined and sorted), `kubelet` (`match` or `mismatch`), `kubelet_sha256` (the digest of the running binary) and `image` (the full pinned image reference).

## Constraints

- Do not change the bundle files.
- Do not run any bundle binary.

## How the answer is checked

The grader runs three checks. Every check first confirms that the manifest signature still verifies, recomputes the binary digests on the control plane node and needs exactly one of them to fail, and confirms that the running worker `kubelet` still matches the manifest.

- `approved-binaries` lists `/var/lib/training-release/approved` and needs exactly the verified binary there, with the digest from the manifest.
- `relay-pinned` reads `relay` and needs a busybox image pinned with `@sha256:`, the rollout complete with one ready replica, and the running pod's image ID ending in the same digest. This check is worth two points.
- `verification-report` needs the `relay` image pinned with `@sha256:` and reads the ConfigMap. Each key must hold the value the grader computes itself, and `image` must equal the image in the Deployment.

Hint: the pod status shows the digest of the image it runs.
