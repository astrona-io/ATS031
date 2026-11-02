---
draft: true
exam_objectives:
- Verify platform binaries before deploying
---
# Verify Signed Artifact Checksums

Verify a signed checksum manifest and reject altered bytes before using a binary.

## Starting state

The isolated environment has two healthy probe replicas, an internal Service and two client Pods. The required result has not been configured.

Use a host shell with the private kubeconfig for this independent kind environment. A kubeconfig identifies the cluster and credentials used by kubectl, the Kubernetes command-line tool.

```sh
export KUBECONFIG="$(astrona kubeconfig ats-031-lab-050-01-01)"
test "$(kubectl config current-context)" = "kind-astro-ats-031-lab-050-01-01" || exit 1
node_name="astro-ats-031-lab-050-01-01-control-plane"
worker_name="astro-ats-031-lab-050-01-01-worker"
```

Keep this connection selected. Host-level commands name only this environment's node containers. They do not operate on the host operating system.

## Required result

Use the public key provisioned with the isolated fixture to verify checksums.sig over checksums.txt. Verify the staged kubectl digest matches the authenticated manifest and the tampered copy does not. Record artifact-review with result verified, tampered rejected and the exact sha256. The fixture key is a local exercise trust root, not proof of the upstream Kubernetes publisher identity.

## Verify The Result

The grader checks the required object fields and actual observations. Wait for controller convergence before submitting. Preserve the task's namespace, workload names and unrelated components.
