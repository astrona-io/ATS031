---
exam_objectives:
- Properly set up Ingress with TLS
---
# Starting Environment

The namespace `starfleet-031-030-04-03` holds the Services `vault` and `beacon`, their TLS Secrets and the Ingresses `vault` and `beacon` on the `websecure` entrypoint. The Secret `crew-client` holds a client certificate (`tls.crt`), its key (`tls.key`) and the crew CA certificate (`ca.crt`). Traefik reads `dynamic.yaml` from the ConfigMap `traefik-dynamic` in `ingress-system`. Its pod also mounts the ConfigMap `client-ca` at `/etc/traefik/client-ca`, but that ConfigMap does not exist yet.

Create the ConfigMap `client-ca` in `ingress-system` with the crew CA certificate under the key `client-ca.crt`. Add a TLS option named `mtls` to `dynamic.yaml` that sets `clientAuthType: RequireAndVerifyClientCert` and reads the CA from `/etc/traefik/client-ca/client-ca.crt`; keep the option `default`. Attach the option only to the Ingress `vault` with the annotation `traefik.ingress.kubernetes.io/router.tls.options: mtls@file`. Restart Traefik so it mounts the new ConfigMap.
