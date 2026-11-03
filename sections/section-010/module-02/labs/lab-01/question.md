---
draft: true
exam_objectives:
- Use Network security policies to restrict cluster level access
---
# Apply A Default-Deny Baseline And Allow One Path

The `outpost` namespace must stop accepting and sending traffic by default, and only one path may stay open: the `shuttle` pod sends requests to the `probe` pods on port 8080.

## Objective

Apply a combined default-deny baseline to `outpost` and add the allow rules for one path, then prove the allowed and the denied paths with requests.

## Starting state

The cluster has three namespaces, `starfleet`, `outpost` and `dock`. Each one runs the `probe` Deployment (two pods, port 8080), the `probe` Service (port 80) and a `shuttle` client pod with `wget`. No NetworkPolicy exists. Calico enforces policy in this cluster.

Use a host shell with this lab's private kubeconfig. A kubeconfig identifies the cluster and credentials used by kubectl, the Kubernetes command-line tool. This environment is separate from the ungraded playground.

```sh
export KUBECONFIG="$(astrona kubeconfig ats-031-lab-010-02-01)"
test "$(kubectl config current-context)" = "kind-astro-ats-031-lab-010-02-01" || exit 1
```

Keep this connection selected throughout the task. Every script supplied by the lab refuses a different context.

## Required result

Work in the `outpost` namespace only. Create these three NetworkPolicy objects:

1. `default-deny-all`: selects all pods and isolates them for both ingress and egress, with `policyTypes` listing `Ingress` and then `Egress`, and no rules.
2. `probe-ingress-from-shuttle`: selects pods labelled `app: probe`, ingress only, and allows pods labelled `app: shuttle` in the same namespace on TCP port 8080.
3. `shuttle-egress-to-probe`: selects pods labelled `app: shuttle`, egress only, with exactly two rules. The first allows pods labelled `app: probe` in the same namespace (a `podSelector` only) on TCP port 8080. The second allows DNS: one peer entry with the namespace `kube-system` (by the label `kubernetes.io/metadata.name`) and the pods labelled `k8s-app: kube-dns`, on UDP port 53 and TCP port 53.

Then the following must hold. The `shuttle` pod in `outpost` gets the `probe` response from `http://probe/`. The `shuttle` pod in `starfleet` times out when it requests `http://probe.outpost/`. The `shuttle` pod in `outpost` times out when it requests `http://probe.starfleet/`. The `starfleet` namespace stays open, so its `shuttle` still reaches its own `probe`. Do not change any other namespace and do not recreate the workloads.

## Verify The Result

The grader checks the stated resource fields and live requests. Wait a few seconds after the last change so the network plugin can update its rules, then repeat your own test requests before you submit. Inspect actual results rather than relying on a sample transcript.
