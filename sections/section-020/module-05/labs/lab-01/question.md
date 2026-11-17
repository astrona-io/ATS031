---
draft: true
exam_objectives:
- Use CIS benchmark to review the security configuration of Kubernetes components
  (etcd, kubelet, kubedns, kubeapi)
---
# Close Anonymous And Open Access On The Kubelet

Solve this question on: `terminal`

An audit found that the kubelet on the worker node accepts anonymous requests, authorizes every authenticated request and listens on the unauthenticated read-only port. The kubelet is the node agent that starts the pods of its node and serves an API on the node. Fix these three findings without taking the node out of service. The environment has one control plane node, one worker node, two healthy `probe` replicas and two client pods. A kubeconfig identifies the cluster and credentials used by kubectl, the Kubernetes command-line tool. A copy of the original kubelet file is in `/opt/training/backup` on the worker node.

Use a host shell with the private kubeconfig for this independent kind environment.

```sh
export KUBECONFIG="$(astrona kubeconfig ats-031-lab-020-05-01)"
test "$(kubectl config current-context)" = "kind-astro-ats-031-lab-020-05-01" || exit 1
node_name="astro-ats-031-lab-020-05-01-control-plane"
worker_name="astro-ats-031-lab-020-05-01-worker"
```

Keep this connection selected. Host-level commands name only this environment's node containers. They do not operate on the host operating system.

Allow about 8 minutes for task work. Cluster startup adds time.

## Tasks

1. Make the kubelet on the worker node reject anonymous requests: `authentication.anonymous.enabled` is `false`.
2. Set the kubelet authorization mode to `Webhook`, so that the kubelet asks the API server whether a request is allowed.
3. Close the read-only port: `readOnlyPort` is `0` or absent in the effective configuration.
4. Restart the kubelet and wait until the effective configuration shows the changes.

## Constraints

- Keep the worker node `Ready` and both application replicas available.
- Do not add a key twice to the kubelet file. A duplicate key stops the kubelet.

## How the answer is checked

The grader reads the effective kubelet configuration of the worker node through the API server (the `configz` endpoint) and runs three checks. The first needs `authentication.anonymous.enabled` to be `false`. The second needs `authorization.mode` to be `Webhook`. The third needs `readOnlyPort` to be `0` or absent. Every check also needs the worker node `Ready`, `/readyz` returning `ok`, the `probe` Deployment fully rolled out, the `shuttle` pod running and ready, and a response with `version=v1` when `shuttle` requests `http://probe/`.

Hint: the kubelet reads its file only at start. Read the effective configuration with `kubectl get --raw /api/v1/nodes/<worker>/proxy/configz`.
