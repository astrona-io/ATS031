---
draft: true
exam_objectives:
- Protect node metadata and endpoints
---
# Block Pod Access To The Kubelet Ports

Allow about 8 minutes for the tasks.

Stop the pods of one namespace from reaching the kubelet ports on the nodes while DNS and Services keep working.

## Starting state

The cluster has one control plane node and one worker node. The kubelet on the worker serves its read-only port 10255 on purpose, and both kubelets serve HTTPS on port 10250. The namespaces `starfleet-031-040-03-01`, `outpost-031-040-03-01` and `dock-031-040-03-01` each have a `probe` Deployment and Service on port 80 and a client pod with the `curl` command. The namespace `metadata-stub-031-040-03-01` has a pod `control` that no policy selects. The pods `runtime-peek`, `cri-helper`, `log-reader` and `net-tool` expose host resources. No NetworkPolicy exists.

```sh
export KUBECONFIG="$(astrona kubeconfig ats-031-lab-040-03-01)"
test "$(kubectl config current-context)" = "kind-astro-ats-031-lab-040-03-01" || exit 1
```

Keep this connection selected for the whole task.

## Required result

The pods in `outpost-031-040-03-01` do not need the kubelet. Create a NetworkPolicy in `outpost-031-040-03-01` that applies to every pod in the namespace and prevents them from reaching port 10250 on both nodes and port 10255 on the worker node. DNS and Services must keep working: `drifter` must still reach the `probe` Service in `outpost-031-040-03-01` and the `probe` Service in `starfleet-031-040-03-01` by its full DNS name. Do not change other namespaces: `shuttle` in `starfleet-031-040-03-01` must still reach the read-only port.

## Verify the result

The grader sends live requests from the client pods and reads the objects. Wait a few seconds after you apply a policy, because the network plugin needs a moment to program it. Do not delete or recreate the existing pods unless the task says so.
