---
draft: true
exam_objectives:
- Protect node metadata and endpoints
---
# Summary

A node offers more than the metadata address. The kubelet serves an API on port 10250 that lists pods, reads logs and runs commands, and it can serve a read-only port 10255 with no authentication. From a pod, 401 on the main port means anonymous access is off, 403 means the caller lacks permission, and 200 with data means the request was accepted. The read-only port answers without a credential, so a pod with no Kubernetes permissions can read the pod specifications of its node when that port is on.

A NetworkPolicy closes the pod's path to these ports. One policy selects all pods and allows `0.0.0.0/0` except the addresses of the nodes. DNS and Services stay open. The same effect can come from a list of port ranges with `endPort` that leaves out the kubelet ports. A pod policy does not close the port itself, so the durable fixes are to turn the read-only port off and to keep anonymous authentication off and authorization on Webhook.

A node credential is limited by the node authorizer, which scopes reads to the pods of that node, and by the `NodeRestriction` admission plugin, which scopes writes to the node's own objects and protects labels. A pod that mounts the runtime socket, or a directory that contains it, can control every container on the node as soon as it runs as root, and no network rule sees it. Pods that use the host network are not restricted by pod policy at all, and privileged pods can reach the node by other routes. The way to find them is to list host paths, host network, privileged and host PID settings with `kubectl`, and the way to prevent them is admission control such as the Pod Security `baseline` level.

Outside the cluster, instance settings such as required tokens and a small hop limit, workload identity, node firewalls and Calico host endpoints add layers that NetworkPolicy cannot provide. No single layer is enough, and the cluster is safer when each layer covers the gap of another.

Key facts to remember:

- The kubelet ports are 10250 (HTTPS) and 10255 (read-only HTTP, off on a hardened node).
- A pod policy cannot protect the node ports from other sources, and it does not apply to host network pods.
- The node authorizer and `NodeRestriction` must both be enabled.
- A mount of the runtime socket, or of its directory, is control of the node.

<!-- astrona:playground:destroy -->
