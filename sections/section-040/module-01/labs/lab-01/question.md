---
exam_objectives:
- Protect node metadata and endpoints
---
# Bring A Host-Network Workload Back Under NetworkPolicy

Allow about 7 minutes for the tasks.

Find out why an egress policy does not restrict one workload, and change the workload so that the policy applies to it.

## Starting state

The namespace `starfleet-031-040-01-01` has the `probe` Deployment and Service, the pod `metadata-simulator` (a web server on port 8080 that stands in for a metadata endpoint) and the Deployment `relay` with one client pod. The NetworkPolicy `starfleet-egress` selects every pod in the namespace and allows egress only to the cluster DNS pods and to the `probe` pods on port 8080. The namespace `outpost-031-040-01-01` has the client pod `drifter` and no NetworkPolicy.

```sh
export KUBECONFIG="$(astrona kubeconfig ats-031-lab-040-01-01)"
test "$(kubectl config current-context)" = "kind-astro-ats-031-lab-040-01-01" || exit 1
```

Keep this connection selected for the whole task.

## Required result

An audit found that the `relay` pod can still reach `metadata-simulator`, although `starfleet-egress` should allow only DNS and the `probe` pods. The `relay` workload does not need any setting that gives it access to the network of the node.

Change the `relay` Deployment so that its pod runs in the pod network, where `starfleet-egress` applies to it. Then `relay` must not reach `metadata-simulator`, and it must still reach the `probe` Service by the name `probe`. Keep the Deployment available with one replica. Do not change or delete the NetworkPolicy, `metadata-simulator` or `drifter`.

## Verify the result

The grader reads the `relay` Deployment and its running pod, and sends live requests from that pod to the pod IP address of `metadata-simulator` and to the `probe` Service. It also checks that `drifter` still reaches `metadata-simulator`, so a blocked request cannot come from a stopped server. Wait until the rollout of `relay` has finished before you submit.
