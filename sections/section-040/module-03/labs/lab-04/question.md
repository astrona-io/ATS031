---
exam_objectives:
- Protect node metadata and endpoints
---
# Find Host-Network Pods And Block New Ones

Allow about 8 minutes for the tasks.

A pod with `hostNetwork: true` uses the network namespace of the node, so no NetworkPolicy applies to its traffic. The dock crew wants a list of these pods for review, and no new ones in their namespace.

## Starting state

The cluster has one control plane node and one worker node. The namespaces `dock-031-040-03-04` and `outpost-031-040-03-04` hold six pods. Some of them use the host network. One runs a privileged container but stays on the pod network. No namespace has a Pod Security label.

```sh
export KUBECONFIG="$(astrona kubeconfig ats-031-lab-040-03-04)"
test "$(kubectl config current-context)" = "kind-astro-ats-031-lab-040-03-04" || exit 1
```

Keep this connection selected for the whole task.

## Required result

- Create the ConfigMap `host-network-pods` in `dock-031-040-03-04` with one key, `pods`. Its value has one line for each pod in `dock-031-040-03-04` and `outpost-031-040-03-04` that sets `hostNetwork: true`, in the form `namespace/name`, and nothing else. The order of the lines does not matter.
- Make Pod Security admission enforce the `baseline` level in `dock-031-040-03-04`, so that the API server rejects a new pod with `hostNetwork: true` there and still accepts an ordinary pod.
- Do not delete, change or recreate any of the six pods. The existing pods stay for the review.

## Verify the result

The grader compares the ConfigMap with the live pods. It sends two pods to the API server as a server-side dry run, one with `hostNetwork: true` and one without, and reads which one the API server rejects. A dry run creates nothing.
