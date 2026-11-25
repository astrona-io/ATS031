---
exam_objectives:
- Properly set up Ingress with TLS
---
# Starting Environment

The namespace `starfleet-031-030-02-04` holds the Deployments and Services `beacon` and `scout`, each on port 80. Traefik serves the IngressClass `traefik` on the entrypoints `web` and `websecure`. There is no Ingress.

Create the Ingress `api` in `starfleet-031-030-02-04` with the class `traefik` on the `web` entrypoint, for the host `api.local`. The path `/healthz` with `pathType: Exact` goes to the Service `beacon` on port 80. The path `/v1` with `pathType: Prefix` goes to the Service `scout` on port 80. Add no other paths, so `/healthz/deep`, `/v2` and `/` get `404`.
