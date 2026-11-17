---
draft: true
exam_objectives:
- Use Network security policies to restrict cluster level access
---
# Secure Three Namespaces With Network Policies

Solve this question on: `terminal`

Three teams share one cluster, and Calico enforces NetworkPolicy in it. The `starfleet` namespace runs the `probe` Deployment (two pods labelled `app: probe`, port 8080) behind the `probe` Service (port 80). The `outpost` namespace runs the `shuttle` and `drifter` pods, both with `wget`. The `dock` namespace runs the `telemetry` pod (a web server on port 8080) and the `scout` pod with its ServiceAccount; `python /app/check.py` in `scout` prints one result for `dns` and one for `api`. The policy `probe-from-outpost` already exists in `starfleet` and has a mistake. No other policy exists. Each namespace must be locked down so that only the listed paths stay open.

Use a host shell with this lab's private kubeconfig. A kubeconfig identifies the cluster and credentials used by kubectl, the Kubernetes command-line tool. This environment is separate from the ungraded playground.

```sh
export KUBECONFIG="$(astrona kubeconfig ats-031-capstone-010)"
test "$(kubectl config current-context)" = "kind-astro-ats-031-capstone-010" || exit 1
```

Keep this connection selected throughout the task. Every script supplied by the lab refuses a different context.

Allow about 30 minutes for task work. Cluster startup adds time.

## Tasks

1. Create a policy `default-deny-all` in each of `starfleet`, `outpost` and `dock`. It selects all pods, lists `Ingress` and then `Egress` in `policyTypes`, and has no rules.
2. Repair `probe-from-outpost` in `starfleet`. After the repair it selects pods labelled `app: probe`, covers ingress only, and has one rule with one `from` entry: the namespace named `outpost` (label `kubernetes.io/metadata.name`) and pods labelled `app: shuttle` in the same entry, on TCP port 8080 only.
3. Allow egress for the `shuttle` pod in `outpost`, in any number of policies: pods labelled `app: probe` in the `starfleet` namespace on TCP port 8080 only (the namespace name label and the pod label in one entry); DNS to CoreDNS on UDP and TCP port 53; and the external range `203.0.113.0/24` without the address `203.0.113.99/32`, on TCP port 443 only.
4. Allow egress for the `scout` pod in `dock`, in any number of policies: DNS to CoreDNS on UDP and TCP port 53, and the Kubernetes API server. Find the API server endpoint address and port in the EndpointSlice of the `kubernetes` Service, and allow that address with a `/32` prefix on that port.
5. Prove the result. `shuttle` gets the `probe` response from `http://probe.starfleet/`, and `python /app/check.py` in `scout` prints `dns=ok api=ok`. Requests to port 8080 time out from `drifter` to the `probe` pod address, from `shuttle` to the `telemetry` pod address, and from `scout` to the `probe` pod address.

## Constraints

- Every allow rule needs explicit peers and explicit ports. A rule without peers, an empty peer, a `0.0.0.0/0` peer or a rule without ports fails the egress checks.
- Do not change any workload, ServiceAccount or Role.

## How the answer is checked

The grader runs five checks. Every check also needs the `probe` Deployment fully rolled out and the `shuttle`, `drifter`, `telemetry` and `scout` pods running and ready.

- `default-deny-all` reads the policy in each of the three namespaces and needs an empty pod selector and the policy types `Ingress` and `Egress`, in that order.
- `probe-from-outpost` reads the policy and needs the pod selector `app: probe`, the policy type `Ingress` only, and the single `from` entry for `outpost` and `app: shuttle` on TCP port 8080.
- `shuttle-egress` collects every egress rule that selects `shuttle` and needs the DNS rule, the `probe` rule on TCP 8080 only and the external range rule on TCP 443 only, with no open rule.
- `scout-egress` collects every egress rule that selects `scout` and needs the DNS rule and a `/32` rule for the API server endpoint address and port, with no open rule.
- `traffic-enforced` sends the requests from task 5: the two allowed requests must return their evidence, and the three denied requests must time out. This check is worth two points.

Hint: Calico updates its rules a few seconds after you apply a policy. Repeat your test requests before you submit.
