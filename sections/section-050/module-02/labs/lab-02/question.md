---
draft: true
exam_objectives:
- Verify platform binaries before deploying
---
# Verify The Running kubelet Against A Release Checksum

The `starfleet` worker node must run the released `kubelet`. The release checksums for two versions were staged on the worker node.

## Starting state

Use a host shell with the private kubeconfig for this independent kind environment. A kubeconfig identifies the cluster and credentials used by kubectl, the Kubernetes command-line tool.

```sh
export KUBECONFIG="$(astrona kubeconfig ats-031-lab-050-02-02)"
test "$(kubectl config current-context)" = "kind-astro-ats-031-lab-050-02-02" || exit 1
CONTROL=astro-ats-031-lab-050-02-02-control-plane
WORKER=astro-ats-031-lab-050-02-02-worker
```

Keep this connection selected. Host-level commands name only the node containers of this environment.

## Required result

On the worker node, find the running `kubelet` process, resolve the binary it runs through `/proc/<pid>/exe`, read its version, and compare the digest of that binary with the staged release checksum for that version. The staged checksums are in `/var/lib/training-release/k8s/release` on the worker node. Record the result in a ConfigMap named `kubelet-review` in the `starfleet` namespace with these keys: `version` (the version the kubelet reports, for example `v1.35.0`), `path` (the path that `/proc/<pid>/exe` points to), `sha256` (the digest of the running binary) and `result` (`match` if the digest equals the staged checksum for that version, otherwise `mismatch`).

## Verify The Result

The grader reads the node files and the objects described above and recomputes every digest itself. Do not change the staged files.
