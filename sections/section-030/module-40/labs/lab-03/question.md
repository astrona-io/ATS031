# Require Client Certificates On One Route

In namespace `starfleet-031-030-04-03`, the Traefik Ingress controller serves `https://vault.example.test` (Ingress `vault`) and `https://beacon.example.test` (Ingress `beacon`). The Secret `crew-client` holds a client certificate and, under `ca.crt`, the crew certificate authority (CA) that signed it. Only `vault` must require a client certificate signed by that CA.

1. Create the ConfigMap `client-ca` in `ingress-system` with the crew CA certificate under the key `client-ca.crt`, and add a TLS option `mtls` to `dynamic.yaml` in the ConfigMap `traefik-dynamic` that sets `clientAuthType: RequireAndVerifyClientCert` and reads `/etc/traefik/client-ca/client-ca.crt`. Keep the option `default` without client authentication.
2. Attach the option to the Ingress `vault` only, with the annotation `traefik.ingress.kubernetes.io/router.tls.options: mtls@file`.
3. `https://vault.example.test` must refuse a client without a certificate and answer a client with the `crew-client` certificate, and `https://beacon.example.test` must still answer without one.

Do not change the Ingress `beacon`, the Secrets or the applications.
