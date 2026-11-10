---
draft: true
exam_objectives:
- Protect node metadata and endpoints
---
# Block Pod Access To The Kubelet Ports

Solve this question on: `terminal`

The cluster has one control plane node and one worker node. The kubelet on the worker serves its read-only port 10255 on purpose, and both kubelets serve HTTPS on port 10250. The namespaces `starfleet-031-040-03-01`, `outpost-031-040-03-01` and `dock-031-040-03-01` each have a `probe` Deployment and Service on port 80 and a client pod with the `curl` command. The namespace `metadata-stub-031-040-03-01` has a pod `control` that no policy selects. The pods `runtime-peek`, `cri-helper`, `log-reader` and `net-tool` expose host resources. No NetworkPolicy exists.

The pods in `outpost-031-040-03-01` do not need the kubelet, so they must lose access to the kubelet ports while DNS and Services keep working.

```sh
export KUBECONFIG="$(astrona kubeconfig ats-031-lab-040-03-01)"
test "$(kubectl config current-context)" = "kind-astro-ats-031-lab-040-03-01" || exit 1
```

Keep this connection selected for the whole task.

Allow about 8 minutes for task work. Cluster startup adds time.

## Tasks

1. Find the InternalIP address of each node with `kubectl get nodes -o wide`.
2. Create a NetworkPolicy in `outpost-031-040-03-01` with an empty pod selector, so it applies to every pod in the namespace, that covers egress and blocks port 10250 on both nodes.
3. Make the same egress policy, or a second one, also block port 10255 on the worker node, while all other egress stays allowed.
4. Prove the result. `drifter` in `outpost-031-040-03-01` must fail to reach both kubelet ports, and must still reach the `probe` Service in its own namespace by the name `probe`, and the `probe` Service in `starfleet-031-040-03-01` by its full DNS name `probe.starfleet-031-040-03-01.svc.cluster.local`.

## Constraints

- Do not change other namespaces: `shuttle` in `starfleet-031-040-03-01` and the pod `control` must still reach the read-only port 10255 on the worker.
- Do not delete or recreate the existing pods.

## How the answer is checked

The grader runs three checks. The first sends requests from `drifter` to `https://<node address>:10250/pods` on the worker and on the control plane node, and both must fail to connect. The second sends a request from `drifter` to `http://<worker address>:10255/pods`, which must fail to connect. The third lists the NetworkPolicies in `outpost-031-040-03-01` and needs one with an empty pod selector and `Egress` in its policy types. Every check also needs HTTP status `200` from `drifter` to `http://probe/` and to `http://probe.starfleet-031-040-03-01.svc.cluster.local/`, and HTTP status `200` from `shuttle` in `starfleet-031-040-03-01` and from `control` to the read-only port on the worker.

Hint: an egress rule to `0.0.0.0/0` can list the node addresses in `except`, or a policy can allow every port but the kubelet ports. Wait a few seconds after you apply a policy, because Calico needs a moment to program it.
