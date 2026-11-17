---
draft: true
exam_objectives:
- Use Network security policies to restrict cluster level access
---
# Summary

A policy has three kinds of selector, and each one reads a different object. `spec.podSelector` chooses the protected pods. A `podSelector` in a peer chooses pods, and without a `namespaceSelector` it stays in the namespace of the policy. A `namespaceSelector` chooses namespaces by their labels. The label `kubernetes.io/metadata.name`, set by the API server on every namespace, is the reliable way to select one namespace by name, and no `name` label exists by default.

The form of a peer entry decides its meaning. A `namespaceSelector` alone admits every pod in the matching namespaces. A `podSelector` and a `namespaceSelector` in one entry combine with AND, and the same selectors in two entries combine with OR. One misplaced dash turns a strict rule into a wide one, so test with a client that has only one of the two properties. An `ipBlock` matches by address range with an optional `except` list, stands alone as its own peer type, and suits addresses outside the cluster more than pods.

Ports are the second half of a rule. Each `ports` item has a protocol (TCP by default), a port number or a container port name, and optionally an `endPort` for a numeric range. A missing `ports` list allows all ports for the peers of the rule, and TCP does not cover UDP. A rule always names the pod port, because the node rewrites a Service address to a pod address before the plugin applies the policy.

Policies follow labels. A pod that gains or loses a label joins or leaves the rules that select it, and new pods from a rollout are covered as soon as they exist. This makes labels a security control: anyone who can edit pod or namespace labels can change what a policy allows.

Key facts to remember:

- Fields in one peer entry are AND; separate entries are OR.
- A timeout in a test shows a dropped packet; a refusal shows a closed port.
- `endPort` needs a numeric `port` and a plugin that supports it.
- Select by label and port name, not by pod address or Service address.



## Independent live assessment

Prepare with [Verify CIDR Exceptions And Port Ranges](course-06a-verify-cidr-and-port-boundaries.md). [Enforce An Address Exception And Port Range](labs/lab-03/question.md) uses its own kind environment. The permitted client connects and the excluded address cannot; Every port in the requested range works and adjacent ports remain denied.

<!-- astrona:playground:destroy -->
