---
draft: true
exam_objectives:
- Verify platform binaries before deploying
---
# Verify Signed Artifact Checksums

Solve this question on: `terminal`

A release of `kubectl` is staged on the control plane node in `/var/lib/training-release`. The folder holds the binary `kubectl`, a changed copy `kubectl-tampered`, the checksum manifest `checksums.txt`, its signature `checksums.sig` and the public key `publisher.pub`. The namespace `starfleet-031-050-01-01` has two healthy `probe` replicas, an internal Service and two client pods. Nothing is recorded yet. The key is a local exercise trust root, not proof of the identity of the upstream Kubernetes publisher.

Use a host shell with the private kubeconfig for this independent kind environment. A kubeconfig identifies the cluster and credentials used by kubectl, the Kubernetes command-line tool.

```sh
export KUBECONFIG="$(astrona kubeconfig ats-031-lab-050-01-01)"
test "$(kubectl config current-context)" = "kind-astro-ats-031-lab-050-01-01" || exit 1
node_name="astro-ats-031-lab-050-01-01-control-plane"
worker_name="astro-ats-031-lab-050-01-01-worker"
```

Keep this connection selected. Host-level commands name only this environment's node containers. They do not operate on the host operating system.

Allow about 8 minutes for task work. Cluster startup adds time.

## Tasks

1. On the control plane node, use `publisher.pub` to verify `checksums.sig` over `checksums.txt`, so you know the manifest is authentic.
2. Compare the SHA-256 digest of `kubectl` and of `kubectl-tampered` with the digest in the verified manifest. The first must match and the second must not.
3. Record the ConfigMap `artifact-review` in the namespace `starfleet-031-050-01-01` with the keys `result: verified`, `tampered: rejected` and `sha256`, set to the exact digest from the authenticated manifest.

## Constraints

- Do not change the staged files in `/var/lib/training-release`.
- Keep the namespace, the workload names and the other components as they are.

## How the answer is checked

The grader runs two checks. The first reads the ConfigMap `artifact-review` in `starfleet-031-050-01-01` and needs `result` set to `verified` and `tampered` set to `rejected`. The second needs `sha256` in the same ConfigMap to equal the first field of `checksums.txt`. Both checks first verify the signature again on the control plane node and recompute both digests, and fail if the staged files were changed.

Hint: `openssl dgst -sha256 -verify <public key> -signature <signature> <file>` prints `Verified OK` for a valid signature.
