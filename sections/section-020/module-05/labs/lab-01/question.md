---
draft: true
exam_objectives:
- Use CIS benchmark to review the security configuration of Kubernetes components
  (etcd, kubelet, kubedns, kubeapi)
---
# Close Anonymous And Open Access On The Kubelet

Allow about 8 minutes for the tasks.

An audit found that the kubelet on the worker node accepts anonymous requests, authorizes every authenticated request and listens on the unauthenticated read-only port. Fix these three findings without taking the node out of service.

## Starting state

The isolated environment has one control plane node, one worker node, two healthy probe replicas and two client Pods. A kubeconfig identifies the cluster and credentials used by kubectl, the Kubernetes command-line tool.

Use a host shell with the private kubeconfig for this independent kind environment.

```sh
export KUBECONFIG="$(astrona kubeconfig ats-031-lab-020-05-01)"
test "$(kubectl config current-context)" = "kind-astro-ats-031-lab-020-05-01" || exit 1
node_name="astro-ats-031-lab-020-05-01-control-plane"
worker_name="astro-ats-031-lab-020-05-01-worker"
```

Keep this connection selected. Host-level commands name only this environment's node containers. They do not operate on the host operating system.

## Required result

1. The kubelet on the worker node rejects anonymous requests: `authentication.anonymous.enabled` is `false`.
2. The kubelet authorization mode is `Webhook`.
3. The read-only port is closed: `readOnlyPort` is `0` or absent in the effective configuration.
4. The worker node is `Ready` and both application replicas stay available.

## Verify The Result

The grader reads the effective kubelet configuration through the API server. The kubelet reads its file only at start, so restart the kubelet and wait until the effective configuration shows the change. A duplicate key in the kubelet file stops the kubelet. A copy of the original file is in `/opt/training/backup` on the worker node.
