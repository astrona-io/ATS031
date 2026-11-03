---
draft: true
exam_objectives:
- Protect node metadata and endpoints
---
# Allow The Metadata Address For One Labelled Pod

Block the metadata address for the pods of a namespace and allow it for pods with one label only.

## Starting state

The cluster has the namespaces `starfleet`, `outpost` and `dock`, each with a `probe` Deployment and Service on port 80 and a client pod with the `curl` command. The pod `agent` in `starfleet` has the label `role=cloud-agent`. The namespace `metadata-stub` has the pod `fake-imds`, a fake metadata server on the host network of the worker node at `169.254.169.254` port 80, and a pod `control` that no policy selects. No NetworkPolicy exists.

```sh
export KUBECONFIG="$(astrona kubeconfig ats-031-lab-040-02-02)"
test "$(kubectl config current-context)" = "kind-astro-ats-031-lab-040-02-02" || exit 1
```

Keep this connection selected for the whole task.

## Required result

The pod `agent` in `starfleet` carries the label `role=cloud-agent` and needs the metadata address to do its work. The pod `shuttle` in the same namespace does not. Configure NetworkPolicy in `starfleet` so that `agent` can reach `169.254.169.254` on port 80, `shuttle` cannot, and both pods can still reach the `probe` Service by its name. Use the existing label. Do not add or remove labels, do not delete pods, and do not change other namespaces: `drifter` in `outpost` must still reach the metadata address.

## Verify the result

The grader sends live requests from the client pods and reads the objects. Wait a few seconds after you apply a policy, because the network plugin needs a moment to program it. Do not delete or recreate the existing pods unless the task says so.
