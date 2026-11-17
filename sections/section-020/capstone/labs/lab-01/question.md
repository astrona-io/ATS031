---
draft: true
exam_objectives:
- Use CIS benchmark to review the security configuration of Kubernetes components
  (etcd, kubelet, kubedns, kubeapi)
---
# Remediate A CIS Benchmark Review Across The Control Plane And The Kubelet

Solve this question on: `terminal`

A CIS benchmark review of this cluster lists six findings: one on the API server, two on etcd and three on the kubelet. The isolated environment has one control plane node, one worker node, two healthy `probe` replicas, an internal Service, two client Pods and the Secret `launch-code` in `starfleet`. Fix every finding, keep the cluster serving traffic and record the evidence of the work. Copies of the original manifests and the kubelet file are in `/opt/training/backup` on the nodes.

Use a host shell with the private kubeconfig for this independent kind environment. A kubeconfig identifies the cluster and credentials used by kubectl, the Kubernetes command-line tool.

```sh
export KUBECONFIG="$(astrona kubeconfig ats-031-capstone-020)"
test "$(kubectl config current-context)" = "kind-astro-ats-031-capstone-020" || exit 1
node_name="astro-ats-031-capstone-020-control-plane"
worker_name="astro-ats-031-capstone-020-worker"
```

Keep this connection selected. Host-level commands name only this environment's node containers. They do not operate on the host operating system.

Allow about 35 minutes for task work. Cluster startup adds time.

## Tasks

1. API server: profiling is enabled. Make the effective `kube-apiserver` command contain `--profiling=false`.
2. etcd: the data directory `/var/lib/etcd` has mode `755`. Change it to mode `700`.
3. etcd: Secrets are stored in clear text. Configure encryption at rest with the `aescbc` provider through `--encryption-provider-config=/etc/kubernetes/enc/encryption-config.yaml`, and rewrite the Secret `launch-code` so it is stored encrypted and still returns its original value through the API.
4. Kubelet on the worker node: disable anonymous requests, change the authorization mode from `AlwaysAllow` to `Webhook`, and close the read-only port `10255` (`readOnlyPort` is `0` or absent).
5. Record the work in a ConfigMap named `cis-evidence` in `starfleet`. The keys `apiserver-profiling`, `etcd-data-dir`, `etcd-encryption`, `kubelet-anonymous-auth`, `kubelet-authorization-mode` and `kubelet-read-only-port` each have the value `fixed`. The keys `before` and `after` hold two non-empty texts that describe the state before and after your changes, and they must differ.

## Constraints

- The API server must stay ready, both `probe` replicas must stay available, and the worker node must stay `Ready`.
- The kubelet starts a pod from every file in `/etc/kubernetes/manifests`, so keep backups of static pod manifests elsewhere.
- A duplicate key in the kubelet file stops the kubelet.

## How the answer is checked

The grader runs five checks. Every check also needs the API server to answer `/readyz` with `ok`, the `probe` Deployment fully rolled out, the `shuttle` pod running and getting `version=v1` from `http://probe/`, and the worker node `Ready`.

- `api-profiling` reads the API server pod and needs `--profiling=false` in its command.
- `etcd-data-dir` reads the mode of `/var/lib/etcd` on the control plane node and needs `700`.
- `secret-encryption` needs the encryption provider flag in the API server command, reads `launch-code` straight from etcd and needs the `aescbc` prefix with no clear text value, and reads the Secret through the API to confirm it still holds its original value. This check is worth two points.
- `kubelet-hardening` reads the worker kubelet's effective configuration and needs anonymous authentication off, the mode `Webhook` and the read-only port closed. This check is worth two points.
- `cis-evidence` reads the ConfigMap and needs the six keys set to `fixed` and different, non-empty `before` and `after` texts.

Hint: wait for each component to restart before you move on. The API server can take a minute to come back after a manifest change.
