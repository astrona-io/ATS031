# Terminate TLS At The Ingress And Verify The Server Name

In namespace `starfleet-031-030-01-01`, the Deployment `probe` and its Service `probe` run, and the Traefik Ingress controller runs in `ingress-system`. The TLS Secret `probe-tls` holds a certificate for `probe.local`. Publish the application over HTTPS only for that name.

1. Create an Ingress named `probe` with class `traefik` that routes host `probe.local`, path `/` (type `Prefix`), to Service `probe` port 80.
2. Serve the Ingress on the Traefik entrypoint `websecure` and terminate TLS with the Secret `probe-tls`.
3. A client that trusts the `probe-tls` certificate must get the reply `version=v1` from `https://probe.local` and must reject the certificate for any other server name.

Do not change the Deployment `probe`, the Service `probe` or the Secret `probe-tls`, and keep certificate verification on.
