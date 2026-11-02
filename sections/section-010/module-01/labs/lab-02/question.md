---
draft: true
exam_objectives:
- Use Network security policies to restrict cluster level access
---
# Allow DNS And One Application Dependency

Allow name resolution and application access while denying a healthy unrelated listener. Use the isolated `starfleet` environment to verify the result.

## Objective

Allow name resolution and application access while denying a healthy unrelated listener.

## Starting state

The application and client fixtures are healthy. Complete the required change without replacing unrelated resources.

Use a host shell with this lab's private kubeconfig. A kubeconfig identifies the cluster and credentials used by kubectl, the Kubernetes command-line tool. This environment is separate from the ungraded playground.

```sh
export KUBECONFIG="$(astrona kubeconfig ats-031-lab-010-01-02)"
test "$(kubectl config current-context)" = "kind-astro-ats-031-lab-010-01-02" || exit 1
```

Keep this connection selected throughout the task. Every script supplied by the lab refuses a different context.


## Required result

Create `shuttle-egress` selecting `app: shuttle`. Allow DNS on TCP and UDP port 53 only to kube-system Pods labelled `k8s-app: kube-dns`, and allow TCP 8080 only to same-namespace Pods labelled `app: probe`. Keep a healthy `blocked-server` Pod with a different label. Shuttle must resolve and reach probe, while a direct request to the running blocked server must time out.

## Verify The Result

The grader checks the stated resource fields and live evidence. Wait for controller convergence before submitting. Inspect actual results rather than relying on a sample transcript.
