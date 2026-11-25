# Summary

A node offers a pod more than the metadata address. The kubelet serves an API on port 10250 that lists pods, reads logs and runs commands in containers. It can also serve a read-only port 10255 that needs no authentication.

When a pod sends a request to port 10250 without a credential, the status code tells you how the kubelet is set up. A 401 means anonymous access is off. A 403 means the kubelet knew the caller, but the caller lacks permission. A 200 with data means the kubelet accepted the request. The read-only port answers without a credential, so a pod with no Kubernetes permissions can read the pod specifications of its node when that port is on.

A NetworkPolicy closes the path from the pods to these ports. One policy selects all pods and allows `0.0.0.0/0` except the addresses of the nodes, and DNS and Services stay open. A list of port ranges with `endPort` that leaves out the kubelet ports has the same effect. A pod policy does not close the port itself. The lasting fixes are on the node: turn the read-only port off, keep anonymous authentication off and keep authorization on Webhook.

Two features limit a stolen node credential. The node authorizer limits reads to the objects of the pods on that node. The `NodeRestriction` admission plugin limits writes to the node's own objects and protects labels.

Some pods reach the node without any credential. A pod that mounts the runtime socket, or a directory that holds it, can control every container on the node as soon as it runs as root, and no network rule sees it. A NetworkPolicy does not restrict a pod that uses the host network at all. A privileged pod can reach the node by other routes. You find these pods by listing host paths and the host network, privileged and host PID settings with `kubectl`. You prevent them with admission control, such as the Pod Security `baseline` level.

Outside the cluster, more layers add what NetworkPolicy cannot provide. Instance settings, such as required tokens and a small hop limit, reduce what the metadata service returns. Workload identity makes the node role less valuable. Node firewalls and Calico host endpoints limit who can reach the node ports. No single layer is enough, and the cluster is safer when each layer covers a gap of another.

Key facts to remember:

- The kubelet ports are 10250 (HTTPS) and 10255 (read-only HTTP, off on a hardened node).
- A pod policy cannot protect the node ports from other sources, and it does not apply to host network pods.
- The node authorizer and `NodeRestriction` must both be enabled.
- A mount of the runtime socket, or of its directory, gives control of the node.

<!-- astrona:playground:destroy -->
