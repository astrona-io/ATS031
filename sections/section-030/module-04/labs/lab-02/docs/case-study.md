---
draft: true
exam_objectives:
- Properly set up Ingress with TLS
---
# Starting Environment

Traefik runs in `ingress-system`. The Ingresses `alpha` (host `alpha.example.test`), `bravo`, `charlie` and `delta` exist and send traffic to the Service `probe`. None of them works. The Secrets `alpha-cert`, `bravo-tls`, `charlie-tls` and `delta-tls` exist in `starfleet-031-030-04-02`.

Repair the four Ingresses. Each one must keep its own host name pattern `<name>.example.test` and use class `traefik`. Each must name a Secret in `starfleet-031-030-04-02` whose certificate matches its host and whose key matches its certificate, and the host in `rules` and in `tls` must be the correct name. Preserve the Deployment and the Service, and do not delete an Ingress.
