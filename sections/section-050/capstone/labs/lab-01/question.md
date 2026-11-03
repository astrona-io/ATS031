---
draft: true
exam_objectives:
- Verify platform binaries before deploying
---
# Verify Before You Deploy Capstone

## Scenario

The `starfleet` team received a release bundle for the cluster nodes. The bundle holds two binaries, `kubectl` and `kubeadm`, a manifest of digests named `SHA256SUMS`, a signature `SHA256SUMS.sig` over the manifest, the publisher public key `publisher.pub` and an image reference in `image.txt`. The manifest also lists the digest of the `kubelet` that the worker node must run. The bundle files are on the control plane node in `/var/lib/training-release/bundle`. One of the two binaries was changed after the manifest was signed.

## Starting state

Use a host shell with the private kubeconfig for this independent kind environment. A kubeconfig identifies the cluster and credentials used by kubectl, the Kubernetes command-line tool.

```sh
export KUBECONFIG="$(astrona kubeconfig ats-031-capstone-050)"
test "$(kubectl config current-context)" = "kind-astro-ats-031-capstone-050" || exit 1
CONTROL=astro-ats-031-capstone-050-control-plane
WORKER=astro-ats-031-capstone-050-worker
```

Keep this connection selected. Host-level commands name only the node containers of this environment. The Deployment `relay` in `starfleet` runs `docker.io/library/busybox:1.37.0` by tag.

## Required result

1. Verify the signature of `SHA256SUMS` with `publisher.pub`. Do this before you trust any digest in the manifest.
2. Check `kubectl` and `kubeadm` against the manifest. Copy only the binaries that pass into `/var/lib/training-release/approved` on the control plane node. That directory must hold nothing else.
3. Resolve the binary of the running `kubelet` on the worker node through `/proc/<pid>/exe` and compare its digest with the `kubelet` line of the manifest.
4. Pin the `relay` Deployment to the digest of the image that its pod runs now. Keep the busybox repository in the reference. Wait for the rollout.
5. Record the result in a ConfigMap named `verification-report` in `starfleet` with these keys: `manifest_signature` (`verified`), `genuine` (the approved binary names, comma-joined and sorted), `rejected` (the rejected binary names, comma-joined and sorted), `kubelet` (`match` or `mismatch`), `kubelet_sha256` (the digest of the running binary) and `image` (the full pinned image reference).

Do not change the bundle files. Do not run any bundle binary.

## Verify The Result

The grader checks the signature, recomputes the digests on the nodes and reads the Deployment, the pod and the ConfigMap.
