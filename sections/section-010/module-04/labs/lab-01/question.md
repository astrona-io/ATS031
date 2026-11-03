---
draft: true
exam_objectives:
- Use Network security policies to restrict cluster level access
---
# Repair A Broken Policy Set

The `scout` pod in `starfleet` must resolve names, call the `probe` Service and list pods through the API server. A default-deny baseline protects the namespace, and the policy set around it has several mistakes.

## Objective

Troubleshoot a broken policy set with a fixed method, repair every fault without opening more than needed, and prove the result with the test script and denied requests.

## Starting state

The `starfleet` namespace runs the `probe` Deployment and Service, the `scout` pod, and the `beacon` pod with `hostNetwork: true`. The `outpost` namespace runs the `drifter` pod, which no policy selects. The policies `default-deny-all`, `scout-egress`, `scout-to-probe` and `probe-ingress` exist in `starfleet`. The command `python /app/check.py` inside the `scout` pod prints one result for each of `dns`, `probe` and `api`.

Use a host shell with this lab's private kubeconfig. A kubeconfig identifies the cluster and credentials used by kubectl, the Kubernetes command-line tool. This environment is separate from the ungraded playground.

```sh
export KUBECONFIG="$(astrona kubeconfig ats-031-lab-010-04-01)"
test "$(kubectl config current-context)" = "kind-astro-ats-031-lab-010-04-01" || exit 1
```

Keep this connection selected throughout the task. Every script supplied by the lab refuses a different context.

## Required result

Repair the policy set in the `starfleet` namespace until the command `kubectl -n starfleet exec scout -- python /app/check.py` prints `dns=ok probe=ok api=ok`.

Keep these limits. The policy `default-deny-all` stays unchanged. Do not change any workload, ServiceAccount or Role. Every allow rule needs explicit peers and explicit ports; a rule that allows every address or every port fails the task. The `scout` pod may send DNS queries to CoreDNS on UDP and TCP port 53, TCP port 8080 to pods labelled `app: probe` in `starfleet` (selected with the namespace name label and the pod label in one entry), and its existing API server rule. The `probe` pods may receive TCP port 8080 from pods labelled `app: scout` and from nothing else.

After the repair, the `drifter` pod in `outpost` must time out when it requests the `probe` pod address on port 8080 and the `scout` pod address on port 8080.

## Verify The Result

The grader checks the stated resource fields and live requests. Wait a few seconds after the last change so the network plugin can update its rules, then repeat your own test requests before you submit. Inspect actual results rather than relying on a sample transcript.
