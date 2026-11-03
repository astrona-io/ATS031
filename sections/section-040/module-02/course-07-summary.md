---
draft: true
exam_objectives:
- Protect node metadata and endpoints
---
# Summary

The cloud metadata service is an HTTP server on the link-local address `169.254.169.254`. It answers any request from the machine, including requests from pods, with facts about the instance, user data and temporary credentials for the cloud role of the node. Kubernetes RBAC does not govern this role, so a pod with no Kubernetes permissions can still act as the node toward the cloud provider. The second version of the Amazon Web Services (AWS) service, the header requirements of Google Cloud and Microsoft Azure, and the token hop limit make simple attacks harder, but they do not replace a network rule.

A NetworkPolicy blocks the address when one policy selects all pods for egress and allows `0.0.0.0/0` with the exception `169.254.169.254/32`. DNS, Services and other egress keep working, because the rule excludes only one address. To open the address for chosen pods, add a second policy that selects them by label and allows that one address and port. Policies add up, so labelled pods get the union of both. The label becomes a control, and whoever can create or patch pods can set it.

Correct-looking policies fail in known ways. An allow of `0.0.0.0/0` with no exception blocks nothing. A DNS-only policy blocks too much. A policy in the wrong namespace protects nothing, a wrong mask changes the range, and a pod with `hostNetwork: true` is not selected by pod policy at all.

Proof has a fixed shape. Send the request from a fresh pod in every namespace, list the policies with their selectors and types, and compare the result with the labels of the pods. A request that works for each allowed pod, a request that fails for each denied pod and a control that shows the server is healthy together show that the block is real and not a failure of the server.

Key facts to remember:

- The metadata address is `169.254.169.254`, and the rule for it is `ipBlock` with `except` and the mask `/32`.
- A NetworkPolicy lists allowed traffic only, and several policies on one pod add up.
- A policy covers its own namespace and the pod network only.
- A timeout (`000` from `curl`) is proof only next to a control request that returns `200`.

<!-- astrona:playground:destroy -->
