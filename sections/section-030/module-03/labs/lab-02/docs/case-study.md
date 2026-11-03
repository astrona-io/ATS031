---
draft: true
exam_objectives:
- Properly set up Ingress with TLS
---
# Starting Environment

The namespace `starfleet` holds the `beacon` Deployment and Service and an Ingress `beacon` that names the Secret `beacon-tls`. A Secret with that name exists only in the namespace `outpost`, and its certificate has a Common Name but no Subject Alternative Name.

Make `https://beacon.example.test` work. The Ingress `beacon` must keep class `traefik`, the host `beacon.example.test` and `secretName: beacon-tls`. Create a Secret `beacon-tls` of type `kubernetes.io/tls` in `starfleet` from a certificate that has `beacon.example.test` in its Subject Alternative Name. Do not use the certificate in `outpost`. Preserve the Deployment and the Service.
