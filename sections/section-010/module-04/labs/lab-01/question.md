---
draft: true
exam_objectives:
- Use Network security policies to restrict cluster level access
---
# Repair A Broken Policy Set

Solve this question on: `terminal`

The `starfleet-031-010-04-01` namespace runs the `probe` Deployment (pods labelled `app: probe`, port 8080) and Service, the `scout` pod labelled `app: scout`, and the `beacon` pod with `hostNetwork: true`. The `outpost-031-010-04-01` namespace runs the `drifter` pod, which no policy selects. Calico, the network plugin of this cluster, enforces NetworkPolicy.

The `scout` pod must resolve names, call the `probe` Service and list pods through the API server. The policies `default-deny-all`, `scout-egress`, `scout-to-probe` and `probe-ingress` exist in `starfleet-031-010-04-01`. The default-deny baseline is correct, but the policy set around it has several mistakes. The command `python /app/check.py` inside the `scout` pod prints one result for each of `dns`, `probe` and `api`.

Use a host shell with this lab's private kubeconfig. A kubeconfig identifies the cluster and credentials used by kubectl, the Kubernetes command-line tool. This environment is separate from the ungraded playground.

```sh
export KUBECONFIG="$(astrona kubeconfig ats-031-lab-010-04-01)"
test "$(kubectl config current-context)" = "kind-astro-ats-031-lab-010-04-01" || exit 1
```

Keep this connection selected throughout the task. Every script supplied by the lab refuses a different context.

Allow about 12 minutes for task work. Cluster startup adds time.

## Tasks

1. Run `kubectl -n starfleet-031-010-04-01 exec scout -- python /app/check.py` and read every policy in `starfleet-031-010-04-01`, so you know which dependency fails and which rule is wrong.
2. Repair the egress rules of `scout`. It may send DNS (Domain Name System) queries to CoreDNS (pods labelled `k8s-app: kube-dns` in `kube-system`) on UDP and TCP port 53, TCP port 8080 to pods labelled `app: probe` in `starfleet-031-010-04-01` (selected with the namespace name label `kubernetes.io/metadata.name` and the pod label in one entry), and keep its existing API server rule.
3. Repair the ingress rules of `probe`. The `probe` pods may receive TCP port 8080 from pods labelled `app: scout` and from nothing else.
4. Prove the result. The check command in `scout` prints `dns=ok probe=ok api=ok`. The `drifter` pod in `outpost-031-010-04-01` times out when it requests the `probe` pod address on port 8080 and the `scout` pod address on port 8080.

## Constraints

- The policy `default-deny-all` stays unchanged.
- Do not change any workload, ServiceAccount or Role.
- Every allow rule needs explicit peers and explicit ports. A rule that allows every address or every port fails the task.

## How the answer is checked

The grader runs two checks. The first reads every egress rule that applies to `scout`: no rule may lack peers or ports or match every address, one rule must allow CoreDNS in `kube-system` on UDP and TCP port 53, and one entry must select the namespace `starfleet-031-010-04-01` and the pods `app: probe` together on TCP port 8080. It then runs `python /app/check.py` in `scout` and needs `dns=ok probe=ok api=ok`. The second reads every ingress rule that applies to the `probe` pods: no rule may be open, every peer must be the pod selector `app: scout`, and one rule must allow it on TCP port 8080. It then sends requests from `drifter` to a `probe` pod address and to the `scout` pod address on port 8080, which must both time out after 3 seconds. Both checks also need `default-deny-all` to still select every pod for `Ingress` and `Egress`, the `probe` Deployment fully rolled out, and the `scout`, `beacon` and `drifter` pods running and ready.

Hint: Calico updates its rules a few seconds after you apply a policy. Repeat the check command before you submit.
