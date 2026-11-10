---
draft: true
exam_objectives:
- Properly set up Ingress with TLS
---
# Starting Environment

The cluster runs Traefik in `ingress-system` with the IngressClass `traefik`. The namespace `starfleet-031-030-02-01` holds the Deployments and Services `probe` and `scout`, both on Service port 80. No Ingress exists yet.

Create an Ingress `fleet` in the namespace `starfleet-031-030-02-01` for class `traefik` and host `fleet.local`. Add a `Prefix` rule for `/probe` that sends requests to the Service `probe` on port 80, and a `Prefix` rule for `/scout` that sends requests to the Service `scout` on port 80. A request for any other path on that host must receive a 404 from the controller. Preserve the original Deployments and Services.
