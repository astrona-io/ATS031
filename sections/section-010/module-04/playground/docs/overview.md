---
draft: true
exam_objectives:
- Use Network security policies to restrict cluster level access
---
# Playground Guide: Policy For Real Cluster Traffic

This playground is a `kind` cluster with Kubernetes v1.35 and the Calico network plugin, which enforces NetworkPolicy. It starts with a policy set in `starfleet` that does not work. Each lesson page tells you which commands to run.

The `starfleet` namespace runs the `probe` Deployment and Service, the `scout` pod with its ServiceAccount, and the `beacon` pod with `hostNetwork: true`. The `outpost` namespace runs a `drifter` pod that no policy selects. The policies in `starfleet` are `default-deny-all`, `scout-egress`, `scout-to-probe` and `probe-ingress`.

Useful commands while you work:

- `kubectl -n starfleet exec scout -- python /app/check.py` prints the result for `dns`, `probe` and `api`.
- `kubectl -n starfleet describe networkpolicy` shows what each policy allows.
- `kubectl -n starfleet get pods --show-labels` shows the labels that selectors use.

A timeout means the network plugin dropped the packets. A refusal means a pod answered and nothing listens on that port.
