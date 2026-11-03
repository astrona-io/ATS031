---
draft: true
exam_objectives:
- Use Network security policies to restrict cluster level access
---
# Playground Guide: Default-Deny Baselines

This playground is a `kind` cluster with Kubernetes v1.35 and the Calico network plugin, which enforces NetworkPolicy. No NetworkPolicy exists when it starts. Each lesson page tells you which commands to run.

The cluster has three namespaces, `starfleet`, `outpost` and `dock`. Each one runs a `probe` Deployment with two pods that listen on port 8080, a `probe` Service on port 80 and a `shuttle` client pod with `wget`.

Useful commands while you work:

- `kubectl get networkpolicy --all-namespaces` lists every policy.
- `kubectl -n outpost delete networkpolicy --all` returns a namespace to the open state.
- `kubectl -n dock exec shuttle -- wget -q -T 3 -O- http://probe.starfleet/` sends a request with a three second limit.

A timeout means the network plugin dropped the packets. A refusal means a pod answered and nothing listens on that port.
