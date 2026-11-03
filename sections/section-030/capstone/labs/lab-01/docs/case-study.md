---
draft: true
exam_objectives:
- Properly set up Ingress with TLS
---
# Starting Environment

Traefik runs in `ingress-system` with a ConfigMap `traefik-dynamic` that allows TLS 1.2. The namespace `starfleet` holds the working Services `probe` and `scout`. An Ingress `scout` exists but does not work: it names class `nginx` and sends traffic to the wrong Service. No `probe` Ingress and no TLS Secrets exist.

Create the Secrets `probe-tls` and `scout-tls` of type `kubernetes.io/tls` in `starfleet`, each from a separate certificate with its own host in the Subject Alternative Name. Create the Ingress `probe` and repair the Ingress `scout`, each with class `traefik`, the `websecure` entrypoint, TLS enabled on the router, its own host, a `Prefix` path `/` and the backend Service of the same name on port 80. Set the default TLS option to `VersionTLS13` with `sniStrict: true`. Redirect plain HTTP on the `web` entrypoint to HTTPS. Each host must serve only its own certificate, and the controller must load the new policy.
