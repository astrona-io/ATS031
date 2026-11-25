# Summary

A NetworkPolicy selects a group of pods and lists the connections they may receive (ingress) or make (egress). The API server only stores the policy. The network plugin on each node enforces it. So on a cluster whose plugin ignores NetworkPolicy, the API server accepts every policy, and none of them blocks anything.

Isolation works per pod and per direction. A pod that no policy selects for a direction accepts all traffic in that direction. Once a policy selects it, the pod accepts only what the policies together allow. Policies contain only allow rules. They never conflict, and a new policy can only open more traffic. A connection needs an allowance on both sides wherever a side is isolated: egress at the source and ingress at the destination.

Peers decide who may connect. Selectors inside one `from` or `to` item combine with AND. Separate items combine with OR, so moving one dash can widen a rule a lot. A `podSelector` without a `namespaceSelector` matches only pods in the policy's own namespace. The automatic label `kubernetes.io/metadata.name` picks a namespace by its name. Rules see the pod IP address and the pod port after the Service address was replaced, so a rule needs the container port, not the Service port.

An isolated client also needs DNS, which means UDP and TCP port 53 to the CoreDNS pods. A default-deny policy with `podSelector: {}` isolates every pod in its namespace, and allow policies then add each path that is really needed.

To test a policy, send one request that must pass and one that must fail, from a real client pod. A timeout shows that the plugin dropped the packets. A refusal shows that nothing listens on the port. When a request fails, compare the selectors with the real labels, check both namespaces, and remove the suspect policy to confirm the cause.

Key facts to remember:

- The network plugin enforces policies, not the API server.
- `policyTypes` defaults to `Ingress`. It includes `Egress` only when the policy has an `egress` section.
- Fields in one peer item combine with AND; separate items combine with OR.
- An empty rule `- {}` allows everything; an empty rule list allows nothing.

<!-- astrona:playground:destroy -->
