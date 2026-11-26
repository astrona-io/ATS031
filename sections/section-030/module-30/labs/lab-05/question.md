# Redirect HTTP To HTTPS And Add An HSTS Header

In namespace `starfleet-031-030-03-05`, the Ingress `harbor` routes `harbor.example.test` to the Service `harbor` on the Traefik entrypoint `websecure` with the TLS Secret `harbor-tls`. Traefik in `ingress-system` reads extra dynamic configuration from the key `dynamic.yaml` of the ConfigMap `traefik-dynamic`, which holds the TLS option `default`.

1. Add a headers middleware named `hsts` with `stsSeconds: 300` to `dynamic.yaml` in `traefik-dynamic`, and keep the TLS option `default` with `minVersion: VersionTLS12`.
2. Attach the middleware to the Ingress `harbor` with the annotation `traefik.ingress.kubernetes.io/router.middlewares: hsts@file`, so `https://harbor.example.test` answers with `Strict-Transport-Security: max-age=300`.
3. Add the two arguments to the Deployment `traefik` that redirect every request on the entrypoint `web` to the entrypoint `websecure` with the scheme `https`, so `http://harbor.example.test/cargo` gets a permanent redirect to the same path over HTTPS.

Keep every existing argument of the Deployment `traefik`, and do not change the Deployment or the Service `harbor`.
