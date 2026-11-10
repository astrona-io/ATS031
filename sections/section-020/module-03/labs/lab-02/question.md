---
draft: true
exam_objectives:
- Use CIS benchmark to review the security configuration of Kubernetes components
  (etcd, kubelet, kubedns, kubeapi)
---
# Disable Profiling And Restrict The API Server Manifest

Solve this question on: `terminal`

A benchmark run on this cluster reports two failing checks for the API server: profiling and the permissions of its manifest. The kind cluster has two healthy `probe` replicas and a `shuttle` client pod in the namespace `starfleet-031-020-03-02`. The API server runs as a static pod with profiling at its default value, and its static pod manifest has mode `644`. A copy of every original manifest is in `/opt/training/backup` on the control plane node.

Use a host shell with the private kubeconfig for this independent kind environment. A kubeconfig identifies the cluster and credentials used by kubectl, the Kubernetes command-line tool.

```sh
export KUBECONFIG="$(astrona kubeconfig ats-031-lab-020-03-02)"
test "$(kubectl config current-context)" = "kind-astro-ats-031-lab-020-03-02" || exit 1
NODE=astro-ats-031-lab-020-03-02-control-plane
```

Allow about 8 minutes for task work. Cluster startup adds time.

## Tasks

1. Set the flag `--profiling=false` in `/etc/kubernetes/manifests/kube-apiserver.yaml` on the control plane node.
2. Give the file `/etc/kubernetes/manifests/kube-apiserver.yaml` mode `600` and owner `root:root`.
3. Wait until the API server answers `ok` on `/readyz` and check that the running pod has the new flag.

## Constraints

- Keep every backup outside `/etc/kubernetes/manifests`.
- Keep the API server ready and both `probe` replicas available.

## How the answer is checked

The grader runs two checks. The first reads the command of the running API server pod and needs `--profiling=false` in it. The second reads the mode and owner of `/etc/kubernetes/manifests/kube-apiserver.yaml` on the control plane node and needs `600 root:root`. Both checks also need the API server pod running and ready, `/readyz` returning `ok`, and the `probe` Deployment fully rolled out.
