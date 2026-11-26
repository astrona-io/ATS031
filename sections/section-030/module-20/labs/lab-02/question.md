# Repair The Ingress Controller Class And Its RBAC

Traefik runs as the Deployment `traefik` in namespace `ingress-system`, with the ServiceAccount `traefik` and the ClusterRole `traefik`. The Ingress `cargo` in `starfleet-031-030-02-02` routes host `cargo.local` on the `web` entrypoint with class `traefik`, but the installation has two mistakes and the route does not work.

1. Fix the argument of the Deployment `traefik` that selects the IngressClass, so Traefik watches Ingress objects of class `traefik`.
2. Give the ClusterRole `traefik` read access to EndpointSlices (API group `discovery.k8s.io`), which Traefik needs to find the pod addresses behind a Service. The ClusterRole must grant only `get`, `list` and `watch` and must not use `*`.
3. A plain HTTP request for `cargo.local` must reach the Service `cargo`.

Do not change the Ingress `cargo`, and change no other argument of the Deployment `traefik`.
