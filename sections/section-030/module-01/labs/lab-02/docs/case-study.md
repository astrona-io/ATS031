---
exam_objectives:
- Properly set up Ingress with TLS
---
# Starting Environment

The namespace `starfleet-031-030-01-02` holds the Deployment `relay` and the Service `relay`. The Service listens on port 80 and sends traffic to the container port 8080. Traefik serves the IngressClass `traefik` on the entrypoints `web` and `websecure`. The Ingress `relay` exists, but Traefik does not route it.

Keep the Ingress name `relay`, the host `relay.local`, the `Prefix` path `/` and the `web` entrypoint. The Ingress must name the class `traefik` and send requests to the Service `relay` on its Service port 80. A plain HTTP request with the host `relay.local` must reach `relay`. A request for any other host must still get `404`. Do not change the Deployment or the Service.
