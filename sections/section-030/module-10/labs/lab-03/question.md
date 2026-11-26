# Create A TLS Secret For An Ingress

In namespace `starfleet-031-030-01-03`, the Ingress `vault` for `vault.local` already names the Secret `vault-tls`, but the Secret does not exist, so Traefik serves its own default certificate. Create the certificate, the key and the Secret.

1. Create a self-signed certificate for `vault.local`: it must have `DNS:vault.local` in its Subject Alternative Name (SAN) and be valid for 90 days.
2. Store the certificate and its own private key as the Secret `vault-tls` of type `kubernetes.io/tls`, with the keys `tls.crt` and `tls.key`.
3. A client that trusts only this certificate must get `200` from the Service `vault` at `https://vault.local`.

Do not change the Ingress `vault`, the Deployments or the Services.
