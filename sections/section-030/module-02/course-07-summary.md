---
draft: true
exam_objectives:
- Properly set up Ingress with TLS
---
# Summary

An Ingress stores routing rules, an IngressClass names the controller, and the controller does the routing. Traefik watches the Kubernetes API through its Ingress provider and builds routers from the rules. A router matches the host and the path of a request on an entrypoint, and a Traefik service sends the request to the pod addresses of the Kubernetes Service. An Ingress whose class no controller serves is accepted and ignored.

A Traefik installation is a Namespace, a ServiceAccount, a ClusterRole and its binding, a Deployment, a Service and an IngressClass. The arguments of the container are the static configuration: the providers, the class filter and the entrypoints. The cluster role gives read access to Ingresses, Services, EndpointSlices and Secrets, and the read access to Secrets in all namespaces is the permission to protect.

The `Exact` path type matches only the identical path, and `Prefix` matches whole path elements. When rules overlap, a longer rule wins by default and a priority annotation can change the order. The backend receives the full path unless a middleware changes it. One host can fan out to several Services by path, and `spec.defaultBackend` answers requests that match no rule. A plain `404 page not found` comes from Traefik and means no router matched.

A route is tested with a `Host` header against the Traefik Service, because the host names in the rules are not in DNS. When a route misbehaves, the evidence is in the controller log, the access log and the API router list, and in the Kubernetes Ingress and EndpointSlice objects.

Key facts to remember:

- The Ingress stores rules; the controller routes.
- The backend names the Service port, not the container port.
- A Traefik `404 page not found` means no router matched.
- The Traefik API without authentication shows the whole routing table.

<!-- astrona:playground:destroy -->
