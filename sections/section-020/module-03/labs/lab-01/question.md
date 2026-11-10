---
draft: true
exam_objectives:
- Use CIS benchmark to review the security configuration of Kubernetes components
  (etcd, kubelet, kubedns, kubeapi)
---
# Enable Audit Logging On The API Server

Solve this question on: `terminal`

The API server of this cluster keeps no record of requests. An audit log is a file where the API server writes one event for each request it handles, filtered by an audit policy. The kind cluster has two healthy `probe` replicas and a `shuttle` client pod in the namespace `starfleet-031-020-03-01`, and a control plane node. The API server runs as a static pod, without an audit policy and without an audit log. A policy file is staged on the control plane node at `/opt/training/audit-policy.yaml`, and no component uses it. A copy of every original manifest is in `/opt/training/backup` on the control plane node.

Use a host shell with the private kubeconfig for this independent kind environment. A kubeconfig identifies the cluster and credentials used by kubectl, the Kubernetes command-line tool.

```sh
export KUBECONFIG="$(astrona kubeconfig ats-031-lab-020-03-01)"
test "$(kubectl config current-context)" = "kind-astro-ats-031-lab-020-03-01" || exit 1
NODE=astro-ats-031-lab-020-03-01-control-plane
```

Allow about 15 minutes for task work. Cluster startup adds time.

## Tasks

1. Make the API server static pod use the staged policy through the flag `--audit-policy-file`.
2. Make the API server write the log to a file set with `--audit-log-path` on a host path of the control plane node. Mount the policy file and the log directory into the API server pod.
3. Set the retention flags `--audit-log-maxage`, `--audit-log-maxbackup` and `--audit-log-maxsize`.
4. Wait until the API server answers `ok` on `/readyz`, then send a request and find it in the audit log on the node.

## Constraints

- Keep every backup outside `/etc/kubernetes/manifests`.
- Keep the API server ready and both `probe` replicas available.

## How the answer is checked

The grader runs three checks. The first reads the command of the running API server pod and needs the flag `--audit-policy-file`. The second needs the flags `--audit-log-maxage`, `--audit-log-maxbackup` and `--audit-log-maxsize`. The third needs `--audit-policy-file` and `--audit-log-path`, creates, reads and deletes a test ConfigMap in `starfleet-031-020-03-01`, and then looks for that ConfigMap's name in the audit log file on the control plane node. Every check also needs the API server pod running and ready, `/readyz` returning `ok`, and the `probe` Deployment fully rolled out.

Hint: a wrong path in the manifest stops the API server. Read the kubelet log on the node with `journalctl -u kubelet` if it does not come back.
