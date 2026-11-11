---
draft: true
exam_objectives:
- Use Network security policies to restrict cluster level access
---
# Apply A Default-Deny Baseline And Allow One Path

Solve this question on: `terminal`

The cluster has three namespaces, `starfleet-031-010-02-01`, `outpost-031-010-02-01` and `dock-031-010-02-01`. Each one runs the `probe` Deployment (two pods labelled `app: probe`, port 8080), the `probe` Service (port 80) and a `shuttle` client pod labelled `app: shuttle` with `wget`. No NetworkPolicy exists. Calico, the network plugin of this cluster, enforces policy.

The `outpost-031-010-02-01` namespace must stop accepting and sending traffic by default. Only one path may stay open: the `shuttle` pod sends requests to the `probe` pods on port 8080.

Use a host shell with this lab's private kubeconfig. A kubeconfig identifies the cluster and credentials used by kubectl, the Kubernetes command-line tool. This environment is separate from the ungraded playground.

```sh
export KUBECONFIG="$(astrona kubeconfig ats-031-lab-010-02-01)"
test "$(kubectl config current-context)" = "kind-astro-ats-031-lab-010-02-01" || exit 1
```

Keep this connection selected throughout the task. Every script supplied by the lab refuses a different context.

Allow about 10 minutes for task work. Cluster startup adds time.

## Tasks

1. In `outpost-031-010-02-01`, create the NetworkPolicy `default-deny-all`. It selects all pods, lists `Ingress` and then `Egress` in `policyTypes`, and has no rules.
2. In `outpost-031-010-02-01`, create the NetworkPolicy `probe-ingress-from-shuttle`. It selects the pods labelled `app: probe`, covers ingress only, and allows pods labelled `app: shuttle` in the same namespace on TCP port 8080.
3. In `outpost-031-010-02-01`, create the NetworkPolicy `shuttle-egress-to-probe`. It selects the pods labelled `app: shuttle`, covers egress only, and has exactly two rules. The first allows pods labelled `app: probe` in the same namespace (a `podSelector` only) on TCP port 8080. The second allows DNS (the Domain Name System): one peer entry with the namespace `kube-system` (by the label `kubernetes.io/metadata.name`) and the pods labelled `k8s-app: kube-dns`, on UDP port 53 and TCP port 53.
4. Prove the result. The `shuttle` pod in `outpost-031-010-02-01` gets a response with `version=v1` from `http://probe/`. The `shuttle` pods in `starfleet-031-010-02-01` and `dock-031-010-02-01` time out when they request `http://probe.outpost-031-010-02-01/`. The `shuttle` pod in `outpost-031-010-02-01` times out when it requests `http://probe.starfleet-031-010-02-01/`.

## Constraints

- Work in the `outpost-031-010-02-01` namespace only. Do not change any other namespace.
- The `starfleet-031-010-02-01` namespace stays open, so its `shuttle` still reaches its own `probe`.
- Do not recreate the workloads.
- Every allow rule needs explicit peers and explicit ports.

## How the answer is checked

The grader runs three checks. The first reads the NetworkPolicy `default-deny-all` and needs an empty pod selector with the policy types `Ingress` and `Egress`, then sends requests from `shuttle` in `starfleet-031-010-02-01` and in `dock-031-010-02-01` to `http://probe.outpost-031-010-02-01/`, which must both time out. The second reads the NetworkPolicy `probe-ingress-from-shuttle` and needs the pod selector `app: probe`, the policy type `Ingress` only, and one rule that allows `app: shuttle` on TCP port 8080. The third needs the NetworkPolicy `shuttle-egress-to-probe` and reads every egress rule that applies to `shuttle` in `outpost-031-010-02-01`: there must be exactly two, one DNS rule to `k8s-app: kube-dns` in `kube-system` on UDP and TCP port 53, and one rule to `app: probe` on TCP port 8080 only. No rule may lack peers or ports, or match every address. It then needs `version=v1` from `http://probe/` and a time-out from `http://probe.starfleet-031-010-02-01/`, both sent from `shuttle` in `outpost-031-010-02-01`. Every check also needs the `probe` Deployments and `shuttle` pods in all three namespaces healthy, and the `shuttle` pod in `starfleet-031-010-02-01` must still get `version=v1` from its own `http://probe/`. Each request waits at most 3 seconds.

Hint: Calico updates its rules a few seconds after you apply a policy. Repeat your test requests before you submit.
