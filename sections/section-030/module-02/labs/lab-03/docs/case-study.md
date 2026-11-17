---
exam_objectives:
- Properly set up Ingress with TLS
---
# Starting Environment

The namespace `starfleet-031-030-02-03` holds the Deployment `depot` and the Service `depot` on port 80. Traefik serves the IngressClass `traefik` on the entrypoints `web` (HTTP) and `websecure` (HTTPS). There is no Ingress.

Create the Ingress `depot` in `starfleet-031-030-02-03` with the class `traefik` and the annotation `traefik.ingress.kubernetes.io/router.entrypoints: web`. It has one rule: the host `depot.local` with a `Prefix` path `/` to the Service `depot` on port 80. Every path of `depot.local` must reach `depot` over HTTP. Requests for other hosts and HTTPS requests must get `404`.
