---
draft: true
exam_objectives:
- Use Network security policies to restrict cluster level access
---
# Allow One Pod From Another Namespace

Allow about 7 minutes for the tasks.

The `shuttle` pod in `outpost-031-010-03-01` must reach the `probe` pods in `starfleet-031-010-03-01`. No other pod may reach them.

## Objective

Write one NetworkPolicy with a single combined peer entry and prove with requests that only the intended pod gets through.

## Starting state

The `starfleet-031-010-03-01` and `outpost-031-010-03-01` namespaces each run the `probe` Deployment (two pods, port 8080), the `probe` Service (port 80), a `shuttle` pod and a `drifter` pod. The `dock-031-010-03-01` namespace has a `shuttle` pod and a `telemetry` pod. No NetworkPolicy exists. Calico enforces policy in this cluster.

Use a host shell with this lab's private kubeconfig. A kubeconfig identifies the cluster and credentials used by kubectl, the Kubernetes command-line tool. This environment is separate from the ungraded playground.

```sh
export KUBECONFIG="$(astrona kubeconfig ats-031-lab-010-03-01)"
test "$(kubectl config current-context)" = "kind-astro-ats-031-lab-010-03-01" || exit 1
```

Keep this connection selected throughout the task. Every script supplied by the lab refuses a different context.

## Required result

Create the NetworkPolicy `probe-from-outpost` in the `starfleet-031-010-03-01` namespace. It selects pods labelled `app: probe`, covers ingress only, and has one rule with one `from` entry. That entry holds a `namespaceSelector` for the namespace named `outpost-031-010-03-01` (use the label `kubernetes.io/metadata.name`) and a `podSelector` for pods labelled `app: shuttle`, in the same entry. The rule allows TCP port 8080 only.

Then the following must hold. The `shuttle` pod in `outpost-031-010-03-01` gets the `probe` response from `http://probe.starfleet-031-010-03-01/`. The `drifter` pod in `outpost-031-010-03-01`, the `shuttle` pod in `dock-031-010-03-01` and the `shuttle` pod in `starfleet-031-010-03-01` all time out when they request the same address. Do not change any other namespace.

## Verify The Result

The grader checks the stated resource fields and live requests. Wait a few seconds after the last change so the network plugin can update its rules, then repeat your own test requests before you submit. Inspect actual results rather than relying on a sample transcript.
