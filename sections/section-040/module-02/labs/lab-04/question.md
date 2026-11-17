---
exam_objectives:
- Protect node metadata and endpoints
---
# Close Metadata Gaps Across Namespaces

Allow about 12 minutes for the tasks.

Check which namespaces really block the cloud metadata address, close the gaps, and allow the address for one labelled workload.

## Starting state

The cluster has the namespaces `starfleet-031-040-02-04`, `outpost-031-040-02-04` and `dock-031-040-02-04`, each with a `probe` Deployment and Service on port 80 and a client pod with the `curl` command. The pods `shuttle` and `agent` run in `starfleet-031-040-02-04`, and `agent` has the label `role=cloud-agent`. The pod `drifter` runs in `outpost-031-040-02-04` and the pod `tender` in `dock-031-040-02-04`. The namespace `metadata-stub-031-040-02-04` has the pod `fake-imds`, a fake metadata server on the host network of the worker node at `169.254.169.254` port 80, and a pod `control` that no policy selects. Some NetworkPolicies already exist.

```sh
export KUBECONFIG="$(astrona kubeconfig ats-031-lab-040-02-04)"
test "$(kubectl config current-context)" = "kind-astro-ats-031-lab-040-02-04" || exit 1
```

Keep this connection selected for the whole task.

## Required result

The security team wants the metadata address blocked in all three application namespaces, for the pods that run now and for pods that start later. One workload is the exception: pods with the label `role=cloud-agent` in `starfleet-031-040-02-04` collect node information and need `169.254.169.254` on port 80.

1. In `outpost-031-040-02-04` and `dock-031-040-02-04`, no pod can reach `169.254.169.254`.
2. In `starfleet-031-040-02-04`, pods with `role=cloud-agent` can reach `169.254.169.254` on port 80, and all other pods cannot.
3. Every pod in the three namespaces can still reach the `probe` Service of its namespace by the name `probe`.

Do not add or remove labels, and do not delete pods. Do not change the namespace `metadata-stub-031-040-02-04`.

## Verify the result

The grader sends live requests from the existing client pods. In each namespace it also starts a new pod without labels, sends the same requests from it and removes it again. Wait a few seconds after you change a policy, because the network plugin needs a moment to program it.
