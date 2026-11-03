---
draft: true
exam_objectives:
- Use CIS benchmark to review the security configuration of Kubernetes components
  (etcd, kubelet, kubedns, kubeapi)
---
# Enable Audit Logging On The API Server

The API server of the `starfleet` cluster keeps no record of requests. Turn on audit logging with the staged policy and prove that an event is written.

## Starting state

The kind cluster has two healthy `probe` replicas, a `shuttle` client pod, and a control plane node. The API server runs without an audit policy and without an audit log. A policy file is staged on the control plane node at `/opt/training/audit-policy.yaml`, and no component uses it. A copy of every original manifest is in `/opt/training/backup` on the control plane node.

Use a host shell with the private kubeconfig for this independent kind environment. A kubeconfig identifies the cluster and credentials used by kubectl, the Kubernetes command-line tool.

```sh
export KUBECONFIG="$(astrona kubeconfig ats-031-lab-020-03-01)"
test "$(kubectl config current-context)" = "kind-astro-ats-031-lab-020-03-01" || exit 1
NODE=astro-ats-031-lab-020-03-01-control-plane
```

## Required result

- The API server static pod uses the staged policy through the flag `--audit-policy-file`.
- The API server writes the log to a file set with `--audit-log-path` on a host path of the control plane node.
- The flags `--audit-log-maxage`, `--audit-log-maxbackup` and `--audit-log-maxsize` are set.
- The API server is ready and both `probe` replicas stay available.

Keep every backup outside `/etc/kubernetes/manifests`.

## Verify The Result

The grader reads the flags of the running API server pod, sends a test request, and looks for that request in the audit log on the node. Wait until the API server answers `ok` on `/readyz` before you submit.
