---
draft: true
exam_objectives:
- Use Network security policies to restrict cluster level access
---
# Repair A Two-Entry Peer Rule

The `shuttle` pod in `starfleet` must reach the `probe` pods in `outpost`, but the policy that guards them lets in more pods than intended.

## Objective

Find why an existing policy admits too many peers, repair it so that only the intended pod gets through, and prove the result with requests.

## Starting state

The `starfleet` and `outpost` namespaces each run the `probe` stack, a `shuttle` pod and a `drifter` pod. The `dock` namespace has a `shuttle` pod and a `telemetry` pod. The policy `probe-from-starfleet` already exists in `outpost`. It selects the `probe` pods and allows TCP port 8080.

Use a host shell with this lab's private kubeconfig. A kubeconfig identifies the cluster and credentials used by kubectl, the Kubernetes command-line tool. This environment is separate from the ungraded playground.

```sh
export KUBECONFIG="$(astrona kubeconfig ats-031-lab-010-03-02)"
test "$(kubectl config current-context)" = "kind-astro-ats-031-lab-010-03-02" || exit 1
```

Keep this connection selected throughout the task. Every script supplied by the lab refuses a different context.

## Required result

Repair the existing NetworkPolicy `probe-from-starfleet` in the `outpost` namespace. After the repair it keeps the same name and the same pod selector, covers ingress only, and has one rule with one `from` entry. That entry holds a `namespaceSelector` for the namespace named `starfleet` (use the label `kubernetes.io/metadata.name`) and a `podSelector` for pods labelled `app: shuttle`, in the same entry. The rule allows TCP port 8080 only.

Then the following must hold. The `shuttle` pod in `starfleet` gets the `probe` response from `http://probe.outpost/`. The `drifter` pod in `starfleet`, the `shuttle` pod in `outpost` and the `shuttle` pod in `dock` all time out when they request the same address. Do not create a second policy.

## Verify The Result

The grader checks the stated resource fields and live requests. Wait a few seconds after the last change so the network plugin can update its rules, then repeat your own test requests before you submit. Inspect actual results rather than relying on a sample transcript.
