---
draft: true
exam_objectives:
- Use CIS benchmark to review the security configuration of Kubernetes components
  (etcd, kubelet, kubedns, kubeapi)
---
# Remediate Five Kubelet Benchmark Findings

Solve this question on: `terminal`

A benchmark review of the worker node lists five findings for the kubelet, the node agent that starts the pods of its node. Remediate all of them and keep the node in service. The environment has one control plane node, one worker node, two healthy `probe` replicas and two client pods. A kubeconfig identifies the cluster and credentials used by kubectl, the Kubernetes command-line tool. The environment also has the weak authentication settings from the review, but only the five findings in the tasks are graded. A copy of the original kubelet file is in `/opt/training/backup` on the worker node.

The five findings are: `/var/lib/kubelet/config.yaml` and `/etc/kubernetes/kubelet.conf` on the worker node have mode `644`, and the benchmark requires `600` or stricter; `rotateCertificates` is `false`; `streamingConnectionIdleTimeout` is not set to a useful value; and `tlsMinVersion` is not set.

Use a host shell with the private kubeconfig for this independent kind environment.

```sh
export KUBECONFIG="$(astrona kubeconfig ats-031-lab-020-05-02)"
test "$(kubectl config current-context)" = "kind-astro-ats-031-lab-020-05-02" || exit 1
node_name="astro-ats-031-lab-020-05-02-control-plane"
worker_name="astro-ats-031-lab-020-05-02-worker"
```

Keep this connection selected. Host-level commands name only this environment's node containers. They do not operate on the host operating system.

Allow about 12 minutes for task work. Cluster startup adds time.

## Tasks

1. Set mode `600` on `/var/lib/kubelet/config.yaml` and on `/etc/kubernetes/kubelet.conf` on the worker node.
2. Set `rotateCertificates: true` in the kubelet configuration file.
3. Set `streamingConnectionIdleTimeout` to `5m0s` and `tlsMinVersion` to `VersionTLS12` in the same file.
4. Restart the kubelet and wait until the effective configuration shows your changes.

## Constraints

- Keep the worker node `Ready` and both application replicas available.
- Do not set `protectKernelDefaults`, because a kind node shares the kernel of the host.
- Do not add a key twice to the kubelet file. A duplicate key stops the kubelet, so remove a key before you append it again.

## How the answer is checked

The grader runs four checks. The first reads the file modes with `stat` on the worker node and needs `600` for both `/var/lib/kubelet/config.yaml` and `/etc/kubernetes/kubelet.conf`. The other three read the effective kubelet configuration of the worker node through the API server (the `configz` endpoint): the second needs `rotateCertificates` to be `true`, the third needs `streamingConnectionIdleTimeout` to be `5m0s`, and the fourth needs `tlsMinVersion` to be `VersionTLS12`. Every check also needs the worker node `Ready`, `/readyz` returning `ok`, the `probe` Deployment fully rolled out, the `shuttle` pod running and ready, and a response with `version=v1` when `shuttle` requests `http://probe/`.

Hint: the kubelet reads its file only at start. Read the effective configuration with `kubectl get --raw /api/v1/nodes/<worker>/proxy/configz`.
