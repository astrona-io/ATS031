# Summary

Real workloads need more than the application connection, and name resolution comes first. CoreDNS runs as pods labelled `k8s-app: kube-dns` in the `kube-system` namespace. An egress rule must allow UDP and TCP port 53 to them. It selects the namespace by its automatic name label and the pods by their label, both in the same peer entry. Without this rule, an isolated pod fails every lookup before it opens any connection.

The API server is not a pod, so it needs a different rule. The `kubernetes` Service forwards to an endpoint address, which you find in an EndpointSlice. The network plugin matches the endpoint address and port after the node rewrote the Service address. The rule uses `ipBlock` with a `/32` prefix and the port, and only the pods that need the API should get it.

Services outside the cluster also use an `ipBlock` range, with an optional `except` list. NetworkPolicy has no field for DNS names. It also only opens the network path: role-based access control (RBAC) still decides what a request may do.

A policy has limits. Kubelet probes from the node pass under Calico, but other plugins may apply policy to node traffic. Pods with `hostNetwork: true` use the node address, and pod policy does not select them in the plugin used here. The API has no application-layer rules, no logging and no counters. An allowed connection is neither encrypted nor authenticated.

A fixed method finds the faults in a set of policies. Write the expected table of allowed and blocked paths first, and test each path with requests that have a time limit. Then list and describe the policies, and compare the selectors with the real labels. Check that `policyTypes` and the rule sections match the direction, and confirm that the plugin enforces policy.

Faults hide each other, so test after each change. An audit also lists the namespaces and pods that no policy selects, because those pods accept all traffic.

Key facts to remember:

- DNS needs both UDP and TCP on port 53.
- Allow the API server endpoint address, not only the Service address.
- `hostNetwork` pods and node traffic are outside pod policy.
- A timeout shows a drop; a refusal shows a closed port.

<!-- astrona:playground:destroy -->
