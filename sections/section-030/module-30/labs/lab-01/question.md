# Create A TLS Secret And Serve An Ingress Over HTTPS

In namespace `starfleet-031-030-03-01`, the Deployment `scout` and its Service `scout` (port 80) run, and Traefik runs in `ingress-system` with the entrypoints `web` and `websecure`. No Secret and no Ingress exist for `scout`. Publish `scout` over HTTPS for the name `scout.example.test`.

1. Create a self-signed certificate with `DNS:scout.example.test` in its Subject Alternative Name and store it with its private key as the Secret `scout-tls` of type `kubernetes.io/tls`.
2. Create an Ingress `scout` with class `traefik` that routes host `scout.example.test`, path `/` (type `Prefix`), to Service `scout` port 80 on the entrypoint `websecure`, with one `tls` entry for `scout.example.test` and the Secret `scout-tls`.
3. A client that trusts your certificate must get the `scout` reply from `https://scout.example.test`.

Do not change the Deployment or the Service `scout`, and do not put a wildcard or any other name in the certificate.
