# Create One Certificate For Two Host Names

In namespace `starfleet-031-030-03-03`, the Ingress `depot` routes `depot.example.test` and `www.depot.example.test` to the Service `depot` on the entrypoint `websecure`. Its one `tls` entry covers both names with the Secret `depot-tls`, which does not exist yet.

1. Create one self-signed certificate, valid for 30 days, and store it with its private key as the Secret `depot-tls` of type `kubernetes.io/tls`.
2. The Subject Alternative Name of the certificate must list `DNS:depot.example.test` and `DNS:www.depot.example.test`.
3. A client that trusts the certificate must get the `depot` reply over HTTPS for both host names.

Do not change the Ingress `depot`, the Deployment or the Service `depot`.
