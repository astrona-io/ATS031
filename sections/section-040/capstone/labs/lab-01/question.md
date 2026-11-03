---
draft: true
exam_objectives:
- Protect node metadata and endpoints
---
# Protect The Node

The cluster has the namespaces `starfleet`, `outpost` and `dock`, each with a `probe` Deployment and Service on port 80 and a client pod with the `curl` command: `shuttle` and `agent` in `starfleet`, `drifter` in `outpost` and `tender` in `dock`. The pod `agent` has the label `role=cloud-agent`. The kubelet on the worker node serves the read-only port 10255 on purpose. The namespace `metadata-stub` has `fake-imds`, a fake metadata server on the worker at `169.254.169.254` port 80, and the pod `control` that no policy selects. The Deployment `runtime-peek` in `outpost` mounts the container runtime socket. No NetworkPolicy exists.

```sh
export KUBECONFIG="$(astrona kubeconfig ats-031-capstone-040)"
test "$(kubectl config current-context)" = "kind-astro-ats-031-capstone-040" || exit 1
```

Keep this connection selected for the whole task.

## Required result

The security review of the cluster asks for four results. Deliver all of them in one pass, and keep the existing workloads running.

1. **Metadata.** No pod in `starfleet`, `outpost` or `dock` may reach `169.254.169.254`, except the pod `agent` in `starfleet`, which must reach it on port 80. Select pods by their labels and do not change any label.
2. **Kubelet.** No pod in the three namespaces, including `agent`, may reach port 10250 on either node or port 10255 on the worker node.
3. **Runtime socket.** The Deployment `runtime-peek` in `outpost` must no longer mount the container runtime socket. It must stay available with one ready replica.
4. **Other traffic.** Every client pod must still reach the `probe` Service in its own namespace by its name. DNS must keep working.

The pod `control` in `metadata-stub` is not covered by the task. The grader uses it to confirm that the fake metadata server and the read-only port are still reachable from a pod that has no policy. Do not add a policy there.

## Verify the result

Prove every allowed and every denied path with `curl` from the matching client pod before you finish. The grader sends the same kind of live requests. Wait a few seconds after you apply a policy, because the network plugin needs a moment to program it.
