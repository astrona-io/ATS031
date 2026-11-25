---
exam_objectives:
- Protect node metadata and endpoints
---
# Repair Metadata Policies That Do Not Block

Allow about 10 minutes for the tasks.

Find and repair three NetworkPolicies that were meant to block the cloud metadata address.

## Starting state

The cluster has the namespaces `starfleet-031-040-02-03`, `outpost-031-040-02-03` and `dock-031-040-02-03`. Each has a `probe` Deployment and Service on port 80, a client pod with the `curl` command (`shuttle`, `drifter` and `tender`), and an egress NetworkPolicy called `metadata-guard`. The `starfleet-031-040-02-03` namespace also runs a second client pod, `agent`, with the label `role: cloud-agent`. The namespace `metadata-stub-031-040-02-03` has the pod `fake-imds`, a fake metadata server on the host network of the worker node at `169.254.169.254` port 80, and a pod `control` that no policy selects.

```sh
export KUBECONFIG="$(astrona kubeconfig ats-031-lab-040-02-03)"
test "$(kubectl config current-context)" = "kind-astro-ats-031-lab-040-02-03" || exit 1
```

Keep this connection selected for the whole task.

## Required result

A colleague wrote the three `metadata-guard` policies and reported the metadata address as blocked in all three namespaces. An audit found that this is not true. Repair the policies so that, in each of the three namespaces:

- no pod can reach `169.254.169.254`, including pods that start later;
- every pod can still reach the `probe` Service of its namespace by the name `probe`.

Keep the existing pods and Services. Do not change the namespace `metadata-stub-031-040-02-03`: the pod `control` must still reach the metadata address.

## Verify the result

The grader sends live requests from `shuttle`, `drifter` and `tender`. In each namespace it also starts a new pod without special labels, sends the same requests from it and removes it again. Wait a few seconds after you change a policy, because the network plugin needs a moment to program it.
