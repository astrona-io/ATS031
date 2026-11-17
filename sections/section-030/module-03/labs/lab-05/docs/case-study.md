---
exam_objectives:
- Properly set up Ingress with TLS
---
# Starting Environment

The namespace `starfleet-031-030-03-05` holds the Deployment `harbor`, the Service `harbor` on port 80, the Secret `harbor-tls` and the Ingress `harbor`. The Ingress routes `harbor.example.test` on the `websecure` entrypoint with TLS. Traefik reads extra dynamic configuration from the ConfigMap `traefik-dynamic` in `ingress-system`, key `dynamic.yaml`, which holds the TLS option `default`.

Add the two arguments to the Deployment `traefik` that redirect every request on the entrypoint `web` to the entrypoint `websecure` with the scheme `https`. Keep all existing arguments. Add a headers middleware named `hsts` with `stsSeconds: 300` to `dynamic.yaml` in `traefik-dynamic`, and keep the TLS option `default`. Attach the middleware to the Ingress `harbor` with the annotation `traefik.ingress.kubernetes.io/router.middlewares: hsts@file`.
