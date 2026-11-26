# Require TLS 1.3 And Strict Server Names

The Traefik Ingress controller in `ingress-system` serves `https://probe.example.test` for the Ingress `probe` in `starfleet-031-030-04-01`. Traefik reads its TLS options from the file `dynamic.yaml` in the ConfigMap `traefik-dynamic`. Tighten the TLS option `default` that every route uses.

1. In the ConfigMap `traefik-dynamic`, set the TLS option `default` to `minVersion: VersionTLS13` and `sniStrict: true`, and make Traefik load it.
2. A TLS 1.2 handshake to `probe.example.test` must be refused, while `https://probe.example.test` still answers with the `probe` reply over TLS 1.3.
3. A handshake for the unknown server name `unknown.example.test` must be refused.

Do not change the Ingress `probe`, the Secret `probe-tls` or the application.
