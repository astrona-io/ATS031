---
draft: true
exam_objectives:
- Verify platform binaries before deploying
---
# Find The Binary That Fails Verification

Solve this question on: `terminal`

The release team staged the three binaries `kubectl`, `kubeadm` and `kubelet` for the Starfleet clusters. Each has a published checksum file. One of the three was changed after its checksum was published. The control plane node holds the files in `/var/lib/training-release/k8s/lab`. Each binary has a checksum file named like the binary with the suffix `.sha256`, which holds only the digest.

Use a host shell with the private kubeconfig for this independent kind environment. A kubeconfig identifies the cluster and credentials used by kubectl, the Kubernetes command-line tool.

```sh
export KUBECONFIG="$(astrona kubeconfig ats-031-lab-050-02-01)"
test "$(kubectl config current-context)" = "kind-astro-ats-031-lab-050-02-01" || exit 1
CONTROL=astro-ats-031-lab-050-02-01-control-plane
WORKER=astro-ats-031-lab-050-02-01-worker
```

Keep this connection selected. Host-level commands name only the node containers of this environment.

Allow about 6 minutes for task work. Cluster startup adds time.

## Tasks

1. List the files in `/var/lib/training-release/k8s/lab` on the control plane node.
2. Compute the SHA-256 digest of each of the three binaries and compare it with the digest in its `.sha256` file.
3. Write the file name of the one binary that fails verification, and nothing else, into `/var/lib/training-release/k8s/lab/result.txt` on the control plane node.

## Constraints

- Do not change the staged binaries or their checksum files.
- Do not run the staged binaries.

## How the answer is checked

The grader runs one check. It recomputes the digest of every staged binary on the control plane node, compares each with its `.sha256` file, and needs `result.txt` to hold the name of the binary that fails. The check also fails when the staged files were changed so that not exactly one binary fails verification.

Hint: `sha256sum` prints the digest followed by the file name. Compare only the digest.
