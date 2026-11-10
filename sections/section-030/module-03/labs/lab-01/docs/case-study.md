---
draft: true
exam_objectives:
- Properly set up Ingress with TLS
---
# Starting Environment

The cluster runs Traefik with the entrypoints `web` and `websecure`. The namespace `starfleet-031-030-03-01` holds a working `scout` Deployment and Service on port 80. There is no Secret and no Ingress for `scout`.

Create a self-signed certificate for `scout.example.test` with that name in the Subject Alternative Name. Store it as the Secret `scout-tls` of type `kubernetes.io/tls` in `starfleet-031-030-03-01`. Create an Ingress `scout` for class `traefik` with the host `scout.example.test`, a `Prefix` path `/` to the Service `scout` on port 80, the `websecure` entrypoint, TLS enabled on the router and `scout-tls` in `spec.tls`. A client that trusts your certificate must get the `scout` response for the matching name. Preserve the original Deployment and Service.
