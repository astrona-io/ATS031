---
exam_objectives:
- Properly set up Ingress with TLS
---
# Starting Environment

The namespace `starfleet-031-030-03-03` holds the Deployment `depot`, the Service `depot` on port 80 and the Ingress `depot`. The Ingress routes both names on the `websecure` entrypoint and has one `tls` entry for both names with the Secret name `depot-tls`. The Secret does not exist.

Create one self-signed certificate and its private key. The Subject Alternative Name (SAN) must list `DNS:depot.example.test` and `DNS:www.depot.example.test`, and the certificate must be valid for 30 days. Store the pair as the Secret `depot-tls` of type `kubernetes.io/tls` in `starfleet-031-030-03-03`. Do not change the Ingress.
