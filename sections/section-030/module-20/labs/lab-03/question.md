# Publish One Host Over HTTP Only

In namespace `starfleet-031-030-02-03`, the Deployment `depot` and the Service `depot` (port 80) run. Traefik in `ingress-system` serves the IngressClass `traefik` on the entrypoints `web` (HTTP) and `websecure` (HTTPS). Publish `depot` for one host, over HTTP only.

1. Create an Ingress named `depot` with class `traefik`, the annotation `traefik.ingress.kubernetes.io/router.entrypoints: web` and one rule: host `depot.local`, `Prefix` path `/`, Service `depot` port 80.
2. Every path of `depot.local`, for example `/manifest`, must reach the Service `depot` over HTTP.
3. A request for another host, and an HTTPS request for `depot.local`, must get 404 from Traefik.

Do not change the Deployment or the Service `depot`, and do not add a TLS section to the Ingress.
