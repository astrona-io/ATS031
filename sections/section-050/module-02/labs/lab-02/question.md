---
draft: true
exam_objectives:
- Verify platform binaries before deploying
---
# Verify The Running kubelet Against A Release Checksum

Solve this question on: `terminal`

The Starfleet worker node must run the released `kubelet`. The release checksums for two versions were staged on the worker node in `/var/lib/training-release/k8s/release`. Nobody has compared the running binary with them yet.

Use a host shell with the private kubeconfig for this independent kind environment. A kubeconfig identifies the cluster and credentials used by kubectl, the Kubernetes command-line tool.

```sh
export KUBECONFIG="$(astrona kubeconfig ats-031-lab-050-02-02)"
test "$(kubectl config current-context)" = "kind-astro-ats-031-lab-050-02-02" || exit 1
CONTROL=astro-ats-031-lab-050-02-02-control-plane
WORKER=astro-ats-031-lab-050-02-02-worker
```

Keep this connection selected. Host-level commands name only the node containers of this environment.

Allow about 10 minutes for task work. Cluster startup adds time.

## Tasks

1. On the worker node, find the running `kubelet` process, resolve the binary it runs through `/proc/<pid>/exe`, and read its version.
2. Compute the SHA-256 digest of that binary.
3. Compare the digest with the staged release checksum for that version.
4. Record the result in a ConfigMap named `kubelet-review` in the `starfleet-031-050-02-02` namespace with these keys: `version` (the version the kubelet reports, for example `v1.35.0`), `path` (the path that `/proc/<pid>/exe` points to), `sha256` (the digest of the running binary) and `result` (`match` if the digest equals the staged checksum for that version, otherwise `mismatch`).

## Constraints

- Do not change the staged files.

## How the answer is checked

The grader runs three checks. Each one first finds the running `kubelet` on the worker node, its binary path, version and digest. The first check needs `version` and `path` in `kubelet-review` to match the running kubelet. The second needs `sha256` to equal the digest of the running binary. The third reads the staged checksum for that version under `/var/lib/training-release/k8s/release` and needs `result` to be `match` when the two digests are equal and `mismatch` when they differ.

Hint: `readlink /proc/<pid>/exe` prints the path of the binary a process runs.
