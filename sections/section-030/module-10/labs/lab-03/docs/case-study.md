---
exam_objectives:
- Properly set up Ingress with TLS
---
# Starting Environment

The namespace `starfleet-031-030-01-03` holds the Deployment `vault`, the Service `vault` on port 80 and the Ingress `vault`. The Ingress uses the `websecure` entrypoint and has a `tls` entry for `vault.local` with the Secret name `vault-tls`. The Secret `vault-tls` does not exist.

Create a self-signed certificate and its private key for `vault.local`. The certificate must have `DNS:vault.local` in its Subject Alternative Name (SAN) and must be valid for 90 days. Store the pair as the Secret `vault-tls` of type `kubernetes.io/tls` in `starfleet-031-030-01-03`, with the keys `tls.crt` and `tls.key`. Do not change the Ingress.
