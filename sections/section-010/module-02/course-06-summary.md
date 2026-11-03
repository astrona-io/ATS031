---
draft: true
exam_objectives:
- Use Network security policies to restrict cluster level access
---
# Summary

A Kubernetes cluster is open by default. A pod that no NetworkPolicy selects accepts every connection and makes every connection. A default-deny baseline closes this: its empty `podSelector` selects all pods of the namespace, its `policyTypes` names the direction, and it has no rules, so nothing is allowed. The core NetworkPolicy API has no deny rule, so isolation plus allow rules is the only model.

Ingress and egress are separate directions. A default-deny ingress policy protects servers and leaves egress open. A default-deny egress policy limits what a compromised pod can contact, and it breaks DNS first, because the query to CoreDNS in the `kube-system` namespace is an outgoing connection. A combined policy lists both types. A request that fails after an egress baseline never reaches its destination, so the policies of the source namespace explain the failure.

Policies are additive. The network plugin merges all policies that select a pod into one set of allowed connections, and the name, age or order of a policy has no effect. A connection between two isolated pods needs an egress rule at the source and an ingress rule at the destination. A usable namespace therefore has a baseline, an ingress allow rule for each server, an egress allow rule for each client, and a DNS rule for every pod that resolves names over UDP and TCP port 53.

A baseline is per namespace. A label and a shell loop with `kubectl apply -n` apply one manifest to many namespaces, and `kubectl diff` previews the change without applying it. A namespace without a baseline stays open, and namespaces created later get no baseline on their own.

Key facts to remember:

- An empty `podSelector` selects every pod in the policy namespace.
- A missing `ingress` or `egress` section allows nothing; an empty rule `- {}` allows everything.
- Test the allowed path and the denied path, and use a pod IP address to separate DNS failures from connection failures.
- Apply allow rules before or with the baseline on a namespace that serves traffic.

<!-- astrona:playground:destroy -->
