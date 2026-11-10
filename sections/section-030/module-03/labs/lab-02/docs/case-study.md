---
draft: true
exam_objectives:
- Properly set up Ingress with TLS
---
# Starting Environment

The namespace `starfleet-031-030-03-02` holds the `beacon` Deployment and Service and an Ingress `beacon` that names the Secret `beacon-tls`. A Secret with that name exists only in the namespace `outpost-031-030-03-02`, and its certificate has a Common Name but no Subject Alternative Name.

Make `https://beacon.example.test` work. The Ingress `beacon` must keep class `traefik`, the host `beacon.example.test` and `secretName: beacon-tls`. Create a Secret `beacon-tls` of type `kubernetes.io/tls` in `starfleet-031-030-03-02` from a certificate that has `beacon.example.test` in its Subject Alternative Name. Do not use the certificate in `outpost-031-030-03-02`. Preserve the Deployment and the Service.
