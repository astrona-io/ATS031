# Summary

A node offers endpoints that Kubernetes role-based access control (RBAC) does not govern. The cloud metadata service returns information about the instance, and often credentials of the node identity. The kubelet API on port 10250 can list pods, read logs and run commands, and it has its own authentication and authorization settings. The container runtime socket gives control of every container to anyone who can write to it.

A node identity and a workload identity are separate. RBAC checks the ServiceAccount, and the cloud provider checks the node identity. So when you cut the permissions of a ServiceAccount, the node can still do everything it could do before.

You can read the settings that decide this exposure from the cluster. The `configz` endpoint shows whether the kubelet accepts anonymous requests and which authorization mode it uses. The secure combination is anonymous access off and Webhook authorization on. A list of pods with `hostNetwork` or `hostPath` volumes shows which pods bypass the pod network or can touch the runtime.

A NetworkPolicy filters traffic on the pod network. It does not select host-network pods or node processes, and it does not change the endpoint behind the address. To close a path for a pod, select the pod for egress and allow only its dependencies. This blocks every address you did not list, which a policy that names only the one address you know cannot do. Remember to allow DNS.

Prove the result with three requests. The target answers an unrestricted client, the restricted pod is blocked, and the permitted dependency still works. On a real cloud cluster, combine the network rule with the provider's metadata protections, workload identity, a narrow node role, and admission controls that reject socket mounts and host networking for applications. The playground shows only the network step.

Key facts to remember:

- RBAC does not govern metadata credentials, the kubelet port or runtime sockets.
- A namespaced NetworkPolicy covers the pod network only.
- An allow-list blocks addresses you did not think of; a deny-list does not.
- Prove a block with a working control request, not with a timeout alone.

<!-- astrona:playground:destroy -->
