---
exam_objectives:
- Properly set up Ingress with TLS
---
# Starting Environment

The namespace `starfleet-031-030-04-05` holds the Service `orbit`, the Ingress `orbit` and the Secret `orbit-tls`. The Ingress serves `orbit.example.test` over HTTPS with that Secret. The certificate in `orbit-tls` is valid for two days. The ConfigMap `orbit-previous` keeps a copy of the old certificate for the grader; do not change it.

Create a new private key and a new self-signed certificate for `orbit.example.test` with `DNS:orbit.example.test` in its Subject Alternative Name (SAN), valid for 90 days. Replace the data of the existing Secret `orbit-tls` in place, so the Ingress keeps the same Secret name. Traefik must then serve the new certificate.
