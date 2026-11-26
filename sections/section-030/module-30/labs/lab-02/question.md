# Fix A Missing TLS Secret For An Ingress

In namespace `starfleet-031-030-03-02`, the Ingress `beacon` (class `traefik`, host `beacon.example.test`) names the Secret `beacon-tls`, but that Secret exists only in namespace `outpost-031-030-03-02`, and its certificate has a Common Name and no Subject Alternative Name. Make `https://beacon.example.test` work.

1. Create the Secret `beacon-tls` of type `kubernetes.io/tls` in `starfleet-031-030-03-02` with a certificate and its matching private key.
2. The certificate must be a new one with `DNS:beacon.example.test` in its Subject Alternative Name, and no wildcard or other name.
3. A client that trusts the new certificate must get the `beacon` reply from `https://beacon.example.test`.

Do not change the Ingress `beacon`, the Deployment or the Service `beacon`, and do not reuse the certificate from `outpost-031-030-03-02`.
