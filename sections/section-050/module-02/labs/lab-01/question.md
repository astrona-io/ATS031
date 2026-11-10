---
draft: true
exam_objectives:
- Verify platform binaries before deploying
---
# Find The Binary That Fails Verification

Allow about 6 minutes for the tasks.

The release team staged the three binaries `kubectl`, `kubeadm` and `kubelet` for the Starfleet clusters. Each has a published checksum file. One of the three was changed after its checksum was published.

## Starting state

Use a host shell with the private kubeconfig for this independent kind environment. A kubeconfig identifies the cluster and credentials used by kubectl, the Kubernetes command-line tool.

```sh
export KUBECONFIG="$(astrona kubeconfig ats-031-lab-050-02-01)"
test "$(kubectl config current-context)" = "kind-astro-ats-031-lab-050-02-01" || exit 1
CONTROL=astro-ats-031-lab-050-02-01-control-plane
WORKER=astro-ats-031-lab-050-02-01-worker
```

Keep this connection selected. Host-level commands name only the node containers of this environment.

## Required result

The control plane node holds the files in `/var/lib/training-release/k8s/lab`. Each binary has a checksum file named like the binary with the suffix `.sha256`, which holds only the digest. Find the one binary that fails verification and write its file name, and nothing else, into `/var/lib/training-release/k8s/lab/result.txt` on the control plane node. Do not change the staged binaries or their checksum files. Do not run the staged binaries.

## Verify The Result

The grader reads the node files and the objects described above and recomputes every digest itself. Do not change the staged files.
