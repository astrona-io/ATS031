---
draft: true
exam_objectives:
- Use Network security policies to restrict cluster level access
---
# Summary

Real workloads need more than the application connection. Name resolution comes first. CoreDNS runs as pods labelled `k8s-app: kube-dns` in the `kube-system` namespace, and an egress rule must allow UDP and TCP port 53 to them, selecting the namespace by its automatic name label and the pods by label in the same peer entry. Without this rule an isolated pod fails every lookup before it opens any connection.

The API server is not a pod. The `kubernetes` Service forwards to an endpoint address, found in an EndpointSlice, and the plugin matches the endpoint address and port after the address translation. A rule for it uses `ipBlock` with a `/32` prefix and the port, and it belongs only to the pods that need the API. External services use an `ipBlock` range with an optional `except` list. NetworkPolicy has no field for DNS names, and it only opens the network path: authorization stays with RBAC.

Policy has limits. Kubelet probes from the node pass under Calico, but other plugins may apply policy to node traffic. Pods with `hostNetwork: true` use the node address and are not selected by pod policy in the plugin used here. The API contains no application-layer rules, no logging and no counters, and an allowed connection is neither encrypted nor authenticated.

A fixed method finds faults in a policy set: write the expected table of allowed and blocked paths, test each path with bounded requests, list and describe the policies, compare selectors with real labels, check that `policyTypes` and the rule sections match the direction, and confirm that the plugin enforces policy. Faults hide each other, so test after each change. An audit also lists the namespaces and pods that no policy selects.

Key facts to remember:

- DNS needs both UDP and TCP on port 53.
- Allow the API server endpoint address, not only the Service address.
- `hostNetwork` pods and node traffic are outside pod policy.
- A timeout shows a drop; a refusal shows a closed port.

<!-- astrona:playground:destroy -->
