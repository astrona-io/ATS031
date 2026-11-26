# Repair Four Broken TLS Ingresses

In namespace `starfleet-031-030-04-02`, the Ingresses `alpha`, `bravo`, `charlie` and `delta` must each serve `https://<name>.example.test` through the Traefik Ingress controller to the Service `probe`. Each one is broken in a different way. Repair them so that a client that trusts the certificate of each Ingress's Secret gets the `probe` reply.

1. Repair `alpha`: it must name a TLS Secret that exists and holds the certificate for `alpha.example.test`.
2. Repair `bravo`: the Secret `bravo-tls` must hold a certificate for `bravo.example.test` and the private key that matches it.
3. Repair `charlie`: its rule and its `tls` entry must both use the host `charlie.example.test`.
4. Repair `delta`: it must use the Ingress class `traefik`.

Do not delete and create again any Ingress, and do not change the Deployment or the Service `probe`.
