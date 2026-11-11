---
draft: true
exam_objectives:
- Protect node metadata and endpoints
---
# Protect The Node

Solve this question on: `terminal`

The cluster has the namespaces `starfleet`, `outpost` and `dock`, each with a `probe` Deployment and Service on port 80 and a client pod with the `curl` command: `shuttle` and `agent` in `starfleet`, `drifter` in `outpost` and `tender` in `dock`. The pod `agent` has the label `role=cloud-agent`. The kubelet on the worker node serves the read-only port 10255 on purpose. The namespace `metadata-stub` has `fake-imds`, a fake metadata server on the worker at `169.254.169.254` port 80, and the pod `control` that no policy selects. The Deployment `runtime-peek` in `outpost` mounts the container runtime socket. No NetworkPolicy exists. The security review of the cluster asks for the results below in one pass, with the existing workloads kept running.

Use a host shell with this lab's private kubeconfig. A kubeconfig identifies the cluster and credentials used by kubectl, the Kubernetes command-line tool. This environment is separate from the ungraded playground.

```sh
export KUBECONFIG="$(astrona kubeconfig ats-031-capstone-040)"
test "$(kubectl config current-context)" = "kind-astro-ats-031-capstone-040" || exit 1
```

Keep this connection selected for the whole task.

Allow about 30 minutes for task work. Cluster startup adds time.

## Tasks

1. Block the metadata address. No pod in `starfleet`, `outpost` or `dock` may reach `169.254.169.254`, except the pod `agent` in `starfleet`, which must reach it on port 80. Select pods by their labels.
2. Block the kubelet. No pod in the three namespaces, including `agent`, may reach port 10250 on either node or port 10255 on the worker node.
3. Remove the container runtime socket mount from the Deployment `runtime-peek` in `outpost`. It must stay available with one ready replica.
4. Prove every allowed and every denied path with `curl` from the matching client pod. Every client pod must still reach the `probe` Service in its own namespace by its name, so DNS must keep working.

## Constraints

- Do not change any pod label. `agent` keeps `role=cloud-agent`, and `shuttle` must not gain it.
- Do not add a policy in `metadata-stub`. The grader uses the pod `control` there to confirm that the fake metadata server and the read-only port are still reachable from a pod that no policy selects.
- Keep every client pod running.

## How the answer is checked

The grader runs three checks. Every check also needs `shuttle`, `agent`, `drifter` and `tender` to get `200` from `http://probe/` in their own namespace, `control` to get `200` from the metadata address and the read-only port, the labels on `agent` and `shuttle` unchanged, and every client pod running.

- `metadata-blocked` sends a request to `http://169.254.169.254/latest/meta-data/` from each client pod. The requests from `shuttle`, `drifter` and `tender` must fail, and the request from `agent` must return `200`.
- `kubelet-ports-blocked` sends requests from each of the four client pods to port 10250 on both nodes and port 10255 on the worker node. All twelve requests must fail. This check is worth two points.
- `runtime-socket-removed` reads `runtime-peek` and needs no runtime socket path in its volumes or mounts, and the Deployment rolled out with every replica ready.

Hint: wait a few seconds after you apply a policy, because the network plugin needs a moment to program it.
