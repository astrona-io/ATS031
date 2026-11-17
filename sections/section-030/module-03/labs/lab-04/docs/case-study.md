---
exam_objectives:
- Properly set up Ingress with TLS
---
# Starting Environment

The namespace `starfleet-031-030-03-04` holds the Deployment `relay`, the Service `relay` on port 80 and the Ingress `relay`. The Ingress routes `relay.example.test` on the `websecure` entrypoint and names the Secret `relay-tls`, which does not exist. The Secret `lab-ca` of type `kubernetes.io/tls` holds the CA certificate in `tls.crt` and the CA private key in `tls.key`.

Create a new private key and a certificate signing request (CSR) for `relay.example.test`. Sign it with the CA from the Secret `lab-ca`, for 30 days, so that the signed certificate has `DNS:relay.example.test` in its Subject Alternative Name (SAN). Store the signed certificate and its key as the Secret `relay-tls` of type `kubernetes.io/tls` in `starfleet-031-030-03-04`. Do not change the Ingress or the Secret `lab-ca`.
