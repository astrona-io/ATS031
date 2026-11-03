---
draft: true
exam_objectives:
- Use CIS benchmark to review the security configuration of Kubernetes components
  (etcd, kubelet, kubedns, kubeapi)
---
# Disable Profiling And Restrict The API Server Manifest

A benchmark run on the `starfleet` cluster reports two failing checks for the API server: profiling and the permissions of its manifest.

## Starting state

The kind cluster has two healthy `probe` replicas and a `shuttle` client pod. The API server runs with profiling at its default value, and its static pod manifest has mode `644`. A copy of every original manifest is in `/opt/training/backup` on the control plane node.

Use a host shell with the private kubeconfig for this independent kind environment. A kubeconfig identifies the cluster and credentials used by kubectl, the Kubernetes command-line tool.

```sh
export KUBECONFIG="$(astrona kubeconfig ats-031-lab-020-03-02)"
test "$(kubectl config current-context)" = "kind-astro-ats-031-lab-020-03-02" || exit 1
NODE=astro-ats-031-lab-020-03-02-control-plane
```

## Required result

- The API server runs with `--profiling=false`.
- The file `/etc/kubernetes/manifests/kube-apiserver.yaml` has mode `600` and owner `root:root`.
- The API server is ready and both `probe` replicas stay available.

## Verify The Result

The grader reads the arguments of the running API server pod and the mode and owner of the manifest on the node. Wait until the API server answers `ok` on `/readyz` before you submit.
