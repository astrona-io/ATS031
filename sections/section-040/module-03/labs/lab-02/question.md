---
draft: true
exam_objectives:
- Protect node metadata and endpoints
---
# Find Pods That Expose The Runtime Or The Host Network

List every pod in the application namespaces that mounts the container runtime socket or uses the host network.

## Starting state

The cluster has one control plane node and one worker node. The kubelet on the worker serves its read-only port 10255 on purpose, and both kubelets serve HTTPS on port 10250. The namespaces `starfleet`, `outpost` and `dock` each have a `probe` Deployment and Service on port 80 and a client pod with the `curl` command. The namespace `metadata-stub` has a pod `control` that no policy selects. The pods `runtime-peek`, `cri-helper`, `log-reader` and `net-tool` expose host resources. No NetworkPolicy exists.

```sh
export KUBECONFIG="$(astrona kubeconfig ats-031-lab-040-03-02)"
test "$(kubectl config current-context)" = "kind-astro-ats-031-lab-040-03-02" || exit 1
```

Keep this connection selected for the whole task.

## Required result

A review needs a list of the pods in `starfleet`, `outpost` and `dock` that either mount the container runtime socket, or a host directory that contains it, or use the host network. Create the ConfigMap `exposed-pods` in the namespace `dock` with one key, `pods`. The value holds one line for each such pod in the form `namespace/name` and nothing else. Include only pods that match. A pod that mounts a different host path does not match. Do not change, delete or recreate any pod.

## Verify the result

The grader sends live requests from the client pods and reads the objects. Wait a few seconds after you apply a policy, because the network plugin needs a moment to program it. Do not delete or recreate the existing pods unless the task says so.
