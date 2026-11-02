---
draft: true
exam_objectives:
- Use CIS benchmark to review the security configuration of Kubernetes components
  (etcd, kubelet, kubedns, kubeapi)
---
# Disable API Server Profiling In A Private Node

Review and correct one effective control-plane setting while keeping API access available.

## Starting state

The isolated environment has two healthy probe replicas, an internal Service and two client Pods. The required result has not been configured.

Use a host shell with the private kubeconfig for this independent kind environment. A kubeconfig identifies the cluster and credentials used by kubectl, the Kubernetes command-line tool.

```sh
export KUBECONFIG="$(astrona kubeconfig ats-031-lab-020-01-01)"
test "$(kubectl config current-context)" = "kind-astro-ats-031-lab-020-01-01" || exit 1
node_name="astro-ats-031-lab-020-01-01-control-plane"
worker_name="astro-ats-031-lab-020-01-01-worker"
```

Keep this connection selected. Host-level commands name only this environment's node containers. They do not operate on the host operating system.

## Required result

Set the isolated API server flag `--profiling=false`. Create ConfigMap `benchmark-review` recording `component: kube-apiserver`, `control: disable-profiling` and `result: corrected`. Keep the API ready and both application replicas available. This is one scoped configuration review, not a claim of full Center for Internet Security (CIS) benchmark compliance.

## Verify The Result

The grader checks the required object fields and actual observations. Wait for controller convergence before submitting. Preserve the task's namespace, workload names and unrelated components.
