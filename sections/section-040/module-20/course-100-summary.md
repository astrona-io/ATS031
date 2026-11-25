# Summary

The cloud metadata service is an HTTP server on the link-local address `169.254.169.254`. It answers any request from the machine, including requests from pods. It returns facts about the instance, user data and temporary credentials for the cloud role of the node.

Kubernetes role-based access control (RBAC) does not control this cloud role. So a pod with no Kubernetes permissions can still act as the node toward the cloud provider. The second version of the Amazon Web Services (AWS) service, the header rules of Google Cloud and Microsoft Azure, and the token hop limit make simple attacks harder. They do not replace a network rule.

A NetworkPolicy blocks the address when it selects all pods for egress and allows `0.0.0.0/0` with the exception `169.254.169.254/32`. DNS, Services and other egress keep working, because the rule leaves out only one address.

To open the address for chosen pods, you add a second policy. It selects those pods by a label and allows that one address and port. Policies add up, so a labelled pod gets the union of both. The label then becomes a security control, and anyone who can create or patch pods can set it.

Policies that look correct fail in known ways. An allow of `0.0.0.0/0` with no exception blocks nothing. A policy that allows only DNS blocks too much. A policy in the wrong namespace protects nothing, and a wrong mask changes the range. Pod policy does not apply at all to a pod with `hostNetwork: true`.

Proof has a fixed shape. Send the request from a fresh pod in every namespace, list the policies with their selectors and types, and compare the result with the labels of the pods. Together, three results show that the block is real and not a failed server: a request that works for each allowed pod, a request that fails for each denied pod, and a control request that gets an answer.

Key facts to remember:

- The metadata address is `169.254.169.254`, and the rule for it is an `ipBlock` with `except` and the mask `/32`.
- A NetworkPolicy lists allowed traffic only, and several policies on one pod add up.
- A policy covers only its own namespace and only the pod network.
- A timeout (`000` from `curl`) is proof only next to a control request that returns `200`.

<!-- astrona:playground:destroy -->
