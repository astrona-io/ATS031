# Rotate An Expiring Certificate

In namespace `starfleet-031-030-04-05`, the Traefik Ingress controller serves `https://orbit.example.test` (Ingress `orbit`) with the certificate in the Secret `orbit-tls`, which expires in two days. The ConfigMap `orbit-previous` keeps a copy of that old certificate. Rotate the certificate without changing the Ingress.

1. Create a new self-signed certificate for `orbit.example.test` with `DNS:orbit.example.test` in its Subject Alternative Name (SAN), valid for 90 days.
2. Store it with a new private key in the existing Secret `orbit-tls`, replacing the data in place so the key matches the certificate.
3. Traefik must serve the new certificate for `https://orbit.example.test`, and the Ingress `orbit` must keep the Secret name `orbit-tls`.

Do not delete and create again the Secret `orbit-tls`, and do not change the ConfigMap `orbit-previous`, the Ingress or the application.
