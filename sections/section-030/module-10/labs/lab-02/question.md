# Fix An Ingress That Traefik Ignores

In namespace `starfleet-031-030-01-02`, the Ingress `relay` for `relay.local` exists, but every request to Traefik returns `404 Not Found`. The Service `relay` listens on port 80 and sends traffic to container port 8080. Fix the Ingress so Traefik routes it.

1. The Ingress `relay` must name the IngressClass `traefik`.
2. The Ingress must send the `Prefix` path `/` of host `relay.local` to the Service `relay` on its Service port 80, on the Traefik entrypoint `web`.
3. A plain HTTP request to Traefik with the host `relay.local` must get `200` from `relay`, and a request for any other host must still get `404`.

Keep the Ingress name `relay`, and do not change the Deployments or the Services.
