---
draft: true
exam_objectives:
- Use Network security policies to restrict cluster level access
---
# Playground Guide: Selecting Peers And Ports

This playground is a `kind` cluster with Kubernetes v1.35 and the Calico network plugin, which enforces NetworkPolicy. No NetworkPolicy exists when it starts. Each lesson page tells you which commands to run.

The cluster has three namespaces. `starfleet` and `outpost` each run a `probe` Deployment (two pods, port 8080), a `probe` Service (port 80), a `shuttle` pod and a `drifter` pod. The `dock` namespace has a `shuttle` pod and a `telemetry` pod that listens on TCP port 9000 (named `feed`) and UDP port 9001 (named `pulse`).

Useful commands while you work:

- `kubectl get networkpolicy --all-namespaces` lists every policy.
- `kubectl get namespace --show-labels` shows the labels that namespace selectors use.
- `kubectl -n outpost exec shuttle -- wget -q -T 3 -O- http://probe.starfleet/` sends a request with a three second limit.

A timeout means the network plugin dropped the packets. A refusal means a pod answered and nothing listens on that port.
