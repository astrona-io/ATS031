---
draft: true
exam_objectives:
- Properly set up Ingress with TLS
---
# Starting Environment

Traefik reads its TLS options from the ConfigMap `traefik-dynamic` in `ingress-system`. The default option sets `minVersion: VersionTLS12`. The Ingress `probe` and its Secret `probe-tls` in `starfleet` work.

Change the default TLS option so that the minimum version is `VersionTLS13` and `sniStrict` is `true`. Make Traefik load the change. The route `https://probe.example.test` must still answer with the `probe` response over TLS 1.3. A TLS 1.2 handshake must fail and a handshake for the unknown name `unknown.example.test` must fail. Do not change the Ingress, the Secret or the application.
