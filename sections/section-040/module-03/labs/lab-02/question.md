---
draft: true
exam_objectives:
- Protect node metadata and endpoints
---
# Find Pods That Expose The Runtime Or The Host Network

Solve this question on: `terminal`

The cluster has one control plane node and one worker node. The kubelet on the worker serves its read-only port 10255 on purpose, and both kubelets serve HTTPS on port 10250. The namespaces `starfleet-031-040-03-02`, `outpost-031-040-03-02` and `dock-031-040-03-02` each have a `probe` Deployment and Service on port 80 and a client pod with the `curl` command. The namespace `metadata-stub-031-040-03-02` has a pod `control` that no policy selects. The pods `runtime-peek`, `cri-helper`, `log-reader` and `net-tool` expose host resources. No NetworkPolicy exists.

A review needs a list of the pods in `starfleet-031-040-03-02`, `outpost-031-040-03-02` and `dock-031-040-03-02` that either mount the container runtime socket, or a host directory that contains it, or use the host network.

```sh
export KUBECONFIG="$(astrona kubeconfig ats-031-lab-040-03-02)"
test "$(kubectl config current-context)" = "kind-astro-ats-031-lab-040-03-02" || exit 1
```

Keep this connection selected for the whole task.

Allow about 8 minutes for task work. Cluster startup adds time.

## Tasks

1. Find the pods in the three namespaces that mount the container runtime socket, or a host directory that contains it, through a `hostPath` volume. A pod that mounts a different host path does not match.
2. Find the pods in the three namespaces that use the host network.
3. Create the ConfigMap `exposed-pods` in the namespace `dock-031-040-03-02` with one key, `pods`. The value holds one line for each pod you found, in the form `namespace/name`, and nothing else.

## Constraints

- Include only pods that match, and list each pod once.
- Do not change, delete or recreate any pod.

## How the answer is checked

The grader runs two checks. The first reads the key `pods` of the ConfigMap `exposed-pods` in `dock-031-040-03-02` and needs every pod that mounts the container runtime socket. The second reads the same key and needs every pod that uses the host network. Both checks fail when the list has a pod that does not match or names a pod twice, and both need the pods `runtime-peek`, `cri-helper`, `log-reader` and `net-tool` still running.

Hint: `kubectl get pods -A -o json` with `jq` shows `.spec.hostNetwork` and the `hostPath` of each volume.
