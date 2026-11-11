---
draft: true
exam_objectives:
- Use CIS benchmark to review the security configuration of Kubernetes components
  (etcd, kubelet, kubedns, kubeapi)
---
# Disable API Server Profiling In A Private Node

Solve this question on: `terminal`

The namespace `starfleet-031-020-01-01` runs the `probe` Deployment (two healthy replicas) behind an internal Service `probe`, and two client pods. The API server of this cluster runs as a static pod on the control plane node. A static pod is a pod that the kubelet starts from a manifest file in `/etc/kubernetes/manifests` on the node. The API server still runs with profiling at its default value, and no review record exists yet.

Use a host shell with the private kubeconfig for this independent kind environment. A kubeconfig identifies the cluster and credentials used by kubectl, the Kubernetes command-line tool.

```sh
export KUBECONFIG="$(astrona kubeconfig ats-031-lab-020-01-01)"
test "$(kubectl config current-context)" = "kind-astro-ats-031-lab-020-01-01" || exit 1
node_name="astro-ats-031-lab-020-01-01-control-plane"
worker_name="astro-ats-031-lab-020-01-01-worker"
```

Keep this connection selected. Host-level commands name only this environment's node containers. They do not operate on the host operating system.

Allow about 8 minutes for task work. Cluster startup adds time.

## Tasks

1. Read the flags of the running API server pod in `kube-system` and find the profiling setting.
2. Set the flag `--profiling=false` on the API server. Edit its static pod manifest on the control plane node and wait until the API server answers `ok` on `/readyz` again.
3. Create the ConfigMap `benchmark-review` in the namespace `starfleet-031-020-01-01` with the keys `component: kube-apiserver`, `control: disable-profiling` and `result: corrected`.

## Constraints

- Keep the API server ready and both `probe` replicas available.
- Keep the namespace, the workload names and unrelated components as they are.
- This is one scoped configuration review, not a claim of full Center for Internet Security (CIS) benchmark compliance.

## How the answer is checked

The grader runs two checks. The first reads the command of the running API server pod in `kube-system` and needs `--profiling=false` in it. The second reads the ConfigMap `benchmark-review` in `starfleet-031-020-01-01` and needs the keys `component: kube-apiserver`, `control: disable-profiling` and `result: corrected`. Both checks also need the API server pod running and ready, `/readyz` returning `ok`, the `probe` Deployment fully rolled out, and a response with `version=v1` when `shuttle` requests `http://probe/`.

Hint: keep a copy of the manifest outside `/etc/kubernetes/manifests` before you edit it. The kubelet restarts the API server when the file changes, so wait a minute before you check.
