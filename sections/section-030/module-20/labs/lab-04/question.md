# Route An Exact Path And A Prefix Path

In namespace `starfleet-031-030-02-04`, the Deployments and Services `beacon` and `scout` run, each on Service port 80. Traefik in `ingress-system` serves the IngressClass `traefik` on the entrypoints `web` and `websecure`. Publish both Services under the host `api.local` with different path types.

1. Create an Ingress named `api` with class `traefik` and the annotation `traefik.ingress.kubernetes.io/router.entrypoints: web` for host `api.local`, with exactly two paths: `/healthz` (`Exact`) and `/v1` (`Prefix`).
2. `api.local/healthz` must reach the Service `beacon` port 80, and `api.local/healthz/deep` must get 404.
3. `api.local/v1` and every path below it, such as `/v1/ships/7`, must reach the Service `scout` port 80, while `/v2` and `/` get 404.

Do not change the Deployments or Services, and add no other path.
