---
exam_objectives:
- Protect node metadata and endpoints
---
# Allow The Metadata Address For One Labelled Pod

Allow about 8 minutes for the tasks.

Block the metadata address for the pods of a namespace and allow it for pods with one label only.

## Starting state

The cluster has the namespaces `starfleet-031-040-02-02`, `outpost-031-040-02-02` and `dock-031-040-02-02`, each with a `probe` Deployment and Service on port 80 and a client pod with the `curl` command. The pod `agent` in `starfleet-031-040-02-02` has the label `role=cloud-agent`. The namespace `metadata-stub-031-040-02-02` has the pod `fake-imds`, a fake metadata server on the host network of the worker node at `169.254.169.254` port 80, and a pod `control` that no policy selects. No NetworkPolicy exists.

```sh
export KUBECONFIG="$(astrona kubeconfig ats-031-lab-040-02-02)"
test "$(kubectl config current-context)" = "kind-astro-ats-031-lab-040-02-02" || exit 1
```

Keep this connection selected for the whole task.

## Required result

The pod `agent` in `starfleet-031-040-02-02` carries the label `role=cloud-agent` and needs the metadata address to do its work. The pod `shuttle` in the same namespace does not. Configure NetworkPolicy in `starfleet-031-040-02-02` so that `agent` can reach `169.254.169.254` on port 80, `shuttle` cannot, and both pods can still reach the `probe` Service by its name. The rule must follow the label, not the pod names: any pod in the namespace with `role=cloud-agent` gets the address, and any other pod, including pods that start later, does not. Use the existing label. Do not add or remove labels, do not delete pods, and do not change other namespaces: `drifter` in `outpost-031-040-02-02` must still reach the metadata address.

## Verify the result

The grader sends live requests from the existing client pods. It also starts two new pods in `starfleet-031-040-02-02`, one without labels and one with `role=cloud-agent`, sends the same requests from them and removes them again. Wait a few seconds after you apply a policy, because the network plugin needs a moment to program it. Do not delete or recreate the existing pods.
