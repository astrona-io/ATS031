---
draft: true
exam_objectives:
- Use Network security policies to restrict cluster level access
---
# Allow One Peer And Deny Another

Enforce both an allowed same-namespace peer and a denied peer in another namespace. Use the isolated `starfleet` environment to verify the result.

## Objective

Enforce both an allowed same-namespace peer and a denied peer in another namespace.

## Starting state

The application and client fixtures are healthy. Complete the required change without replacing unrelated resources.

Use a host shell with this lab's private kubeconfig. A kubeconfig identifies the cluster and credentials used by kubectl, the Kubernetes command-line tool. This environment is separate from the ungraded playground.

```sh
export KUBECONFIG="$(astrona kubeconfig ats-031-lab-010-01-01)"
test "$(kubectl config current-context)" = "kind-astro-ats-031-lab-010-01-01" || exit 1
```

Keep this connection selected throughout the task. Every script supplied by the lab refuses a different context.


## Required result

Create NetworkPolicy `probe-shuttle` selecting `app: probe` for ingress. Allow only same-namespace Pods labelled `app: shuttle` on TCP port 8080. Keep the original workload and clients healthy. Shuttle must receive version one through the Service; drifter in `outpost` must time out. Do not create any policy that also allows drifter.

## Verify The Result

The grader checks the stated resource fields and live evidence. Wait for controller convergence before submitting. Inspect actual results rather than relying on a sample transcript.
