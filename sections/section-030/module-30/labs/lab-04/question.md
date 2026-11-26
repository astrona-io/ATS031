# Sign A Server Certificate With The Lab CA

In namespace `starfleet-031-030-03-04`, the Ingress `relay` routes `relay.example.test` on the entrypoint `websecure` and names the Secret `relay-tls`, which does not exist. The Secret `lab-ca` holds the certificate authority (CA) certificate in `tls.crt` and the CA private key in `tls.key`.

1. Create a new private key and a certificate signing request for `relay.example.test`, sign it with the CA from `lab-ca` for 30 days, and store the signed certificate and its key as the Secret `relay-tls` of type `kubernetes.io/tls`.
2. The signed certificate must have `DNS:relay.example.test` in its Subject Alternative Name.
3. A client that trusts only the lab CA must get the `relay` reply from `https://relay.example.test`.

Do not change the Ingress `relay`, the Secret `lab-ca` or the ConfigMap `lab-ca-original`.
