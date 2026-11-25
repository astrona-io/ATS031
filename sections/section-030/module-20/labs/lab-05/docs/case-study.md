---
exam_objectives:
- Properly set up Ingress with TLS
---
# Starting Environment

The namespace `starfleet-031-030-02-05` holds the Deployment `beacon` and the Service `beacon`. The Service has one port, named `http`, with the number 80. The Ingress `beacon` routes the host `beacon.local` on the `web` entrypoint, but Traefik builds no route for it. In this lab Traefik runs with its API enabled on port 8080 of the Service `traefik` in `ingress-system`.

Fix the Ingress `beacon` so plain HTTP requests for `beacon.local` reach the Service `beacon`. Keep the host, the path and the entrypoint. Then read the list of HTTP routers from the Traefik API and create the ConfigMap `route-evidence` in `starfleet-031-030-02-05` with the key `router`. Its value is the name of the router whose rule matches `beacon.local`, exactly as the API prints it, including the part after `@`.
