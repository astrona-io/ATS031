---
draft: true
exam_objectives:
- Use Network security policies to restrict cluster level access
---
# Summary

A NetworkPolicy selects pods and lists the connections they may receive (ingress) or make (egress). The API server only stores the object. The network plugin on each node enforces it, so a cluster whose plugin ignores NetworkPolicy accepts policies that do nothing.

Isolation is per pod and per direction. A pod that no policy selects for a direction accepts all traffic in that direction. A pod that some policy selects accepts only what the union of those policies allows. Policies contain only allow rules, so they never conflict and a later policy can only widen access. A connection needs an allowance at the source egress and at the destination ingress wherever those sides are isolated.

Peers decide who is allowed. Selectors inside one `from` or `to` item combine with AND, and separate items combine with OR, so the placement of one dash can widen a rule. A `podSelector` without a `namespaceSelector` matches only the policy's own namespace. The label `kubernetes.io/metadata.name` selects a namespace by name. Rules match the pod IP address and pod port after a Service rewrote the destination, so a rule needs the container port.

An isolated client also needs DNS, which means UDP and TCP port 53 to the CoreDNS pods. A default-deny policy with `podSelector: {}` isolates every pod in its namespace, and allow policies then add each needed path. To test a policy, run one allowed request and one denied request from a pod: a timeout shows that the plugin dropped the packets, and a refusal shows that nothing listens. When a request fails, compare selectors with real labels, check both namespaces and remove the suspect policy to confirm it.

Key facts to remember:

- Enforcement belongs to the network plugin, not to the API server.
- `policyTypes` defaults to `Ingress`, and to `Egress` only when an `egress` section exists.
- Fields in one peer item are AND; separate items are OR.
- An empty rule `- {}` allows everything; an empty list denies everything.

<!-- astrona:playground:destroy -->
