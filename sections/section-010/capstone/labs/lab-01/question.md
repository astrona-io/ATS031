---
draft: true
exam_objectives:
- Use Network security policies to restrict cluster level access
---
# Secure Three Namespaces With Network Policies

Three teams share one cluster. The `starfleet` namespace runs the `probe` application, `outpost` runs a `shuttle` client and a `drifter` pod, and `dock` runs the `scout` agent and a `telemetry` server. Each namespace must be locked down, and only the listed paths may stay open.

## Objective

Build a complete NetworkPolicy set for three namespaces: default-deny baselines, a repaired cross-namespace rule, DNS, an external range and an API server rule. Prove it with allowed and denied requests.

## Starting state

Calico enforces policy in this cluster. The `starfleet` namespace runs the `probe` Deployment (two pods, port 8080) and the `probe` Service (port 80). The `outpost` namespace runs the `shuttle` and `drifter` pods with `wget`. The `dock` namespace runs the `telemetry` pod (a web server on port 8080) and the `scout` pod with its ServiceAccount; `python /app/check.py` in `scout` prints one result for `dns` and one for `api`. The policy `probe-from-outpost` already exists in `starfleet` and has a mistake. No other policy exists.

Use a host shell with this lab's private kubeconfig. A kubeconfig identifies the cluster and credentials used by kubectl, the Kubernetes command-line tool. This environment is separate from the ungraded playground.

```sh
export KUBECONFIG="$(astrona kubeconfig ats-031-capstone-010)"
test "$(kubectl config current-context)" = "kind-astro-ats-031-capstone-010" || exit 1
```

Keep this connection selected throughout the task. Every script supplied by the lab refuses a different context.

## Required result

Create and repair the following. Every allow rule needs explicit peers and explicit ports.

1. A policy `default-deny-all` in each of `starfleet`, `outpost` and `dock`. It selects all pods, lists `Ingress` and then `Egress` in `policyTypes`, and has no rules.
2. Repair `probe-from-outpost` in `starfleet`. After the repair it selects pods labelled `app: probe`, covers ingress only, and has one rule with one `from` entry: the namespace named `outpost` (label `kubernetes.io/metadata.name`) and pods labelled `app: shuttle` in the same entry, on TCP port 8080 only.
3. Egress for the `shuttle` pod in `outpost`, in any number of policies: pods labelled `app: probe` in the `starfleet` namespace on TCP port 8080 only (selected with the namespace name label and the pod label in one entry); DNS to CoreDNS on UDP and TCP port 53; and the external range `203.0.113.0/24` without the address `203.0.113.99/32`, on TCP port 443 only.
4. Egress for the `scout` pod in `dock`, in any number of policies: DNS to CoreDNS on UDP and TCP port 53, and the Kubernetes API server. Find the API server endpoint address and port in the EndpointSlice of the `kubernetes` Service, and allow that address with a `/32` prefix on that port.

Then the following must hold. The `shuttle` pod in `outpost` gets the `probe` response from `http://probe.starfleet/`. The command `python /app/check.py` in the `scout` pod prints `dns=ok api=ok`. The `drifter` pod in `outpost` times out when it requests the `probe` pod address on port 8080. The `shuttle` pod in `outpost` times out when it requests the `telemetry` pod address on port 8080. The `scout` pod times out when it requests the `probe` pod address on port 8080. Do not change any workload, ServiceAccount or Role.

## Verify The Result

The grader checks the stated resource fields and live requests. Wait a few seconds after the last change so the network plugin can update its rules, then repeat your own test requests before you submit. Inspect actual results rather than relying on a sample transcript.
