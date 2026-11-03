---
draft: true
exam_objectives:
- Use CIS benchmark to review the security configuration of Kubernetes components
  (etcd, kubelet, kubedns, kubeapi)
---
# Remediate A CIS Benchmark Review Across The Control Plane And The Kubelet

A CIS benchmark review of this cluster lists six findings: one on the API server, two on etcd and three on the kubelet. Fix all of them, keep the cluster serving traffic and record the evidence of the work.

## Starting state

The isolated environment has one control plane node, one worker node, two healthy probe replicas, an internal Service, two client Pods and the Secret `launch-code` in `starfleet`. A kubeconfig identifies the cluster and credentials used by kubectl, the Kubernetes command-line tool.

Use a host shell with the private kubeconfig for this independent kind environment.

```sh
export KUBECONFIG="$(astrona kubeconfig ats-031-capstone-020)"
test "$(kubectl config current-context)" = "kind-astro-ats-031-capstone-020" || exit 1
node_name="astro-ats-031-capstone-020-control-plane"
worker_name="astro-ats-031-capstone-020-worker"
```

Keep this connection selected. Host-level commands name only this environment's node containers. They do not operate on the host operating system.

## Findings

1. API server: profiling is enabled. The effective `kube-apiserver` command must contain `--profiling=false`.
2. etcd: the data directory `/var/lib/etcd` has mode `755`. It must have mode `700`.
3. etcd: Secrets are stored in clear text. The Secret `launch-code` must be stored encrypted with the `aescbc` provider and must still return its original value through the API.
4. Kubelet: anonymous requests are enabled on the worker node. They must be disabled.
5. Kubelet: the authorization mode is `AlwaysAllow`. It must be `Webhook`.
6. Kubelet: the read-only port `10255` is open. It must be closed (`readOnlyPort` is `0` or absent).

## Evidence

Record the work in a ConfigMap named `cis-evidence` in the namespace `starfleet`. It has these keys:

- `apiserver-profiling`, `etcd-data-dir`, `etcd-encryption`, `kubelet-anonymous-auth`, `kubelet-authorization-mode` and `kubelet-read-only-port`, each with the value `fixed`.
- `before` and `after`: two non-empty text values that describe the state before and after your changes. They must differ.

## Required result

All six findings are fixed in the effective state. The API server is ready, both application replicas stay available, the worker node is `Ready` and the evidence ConfigMap exists.

## Verify The Result

The grader reads the API server pod, the etcd data directory, the stored Secret in etcd, the effective kubelet configuration and the ConfigMap. Edit static pod manifests with care: the kubelet starts a pod from every file in `/etc/kubernetes/manifests`, so keep backups elsewhere. Copies of the original manifests and the kubelet file are in `/opt/training/backup` on the nodes. A duplicate key in the kubelet file stops the kubelet. Wait for each component to restart before you move on.
