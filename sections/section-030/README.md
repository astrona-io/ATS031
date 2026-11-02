---
draft: true
exam_objectives:
- Properly set up Ingress with TLS
---
# Properly set up Ingress with TLS

A client requests `probe.local` over HTTPS. Traefik picks the route, presents a certificate and forwards the request to the `probe` Service. The Ingress object only declares the rules; the controller does the work, and the client decides whether to trust the certificate. This section teaches routing, certificates, the TLS Secret and the checks that prove the right certificate is served.

## Learning Path

1. Set Up Ingress With TLS: the landing page and the playground.
2. Ingress Routing: Controller, Class, Host And Path
3. Certificates And The TLS Secret
4. Configure An Ingress With TLS And Verify It
5. Several Hosts, Server Name Selection And Troubleshooting
6. Summary, then the ten-question knowledge check.

The parts carry the hands-on steps. Each lab follows the part that practises its skill. The playground is a private `kind` cluster with Kubernetes v1.35; launch it from the landing page and keep it running while you read.

## Learning Outcomes

- Explain the roles of the Ingress object, the IngressClass and the Ingress controller.
- Write Ingress rules with host, path, `pathType` and a backend Service port.
- Create a `kubernetes.io/tls` Secret from a certificate and a key, and check that the two match.
- Configure `spec.tls` in an Ingress and explain which certificate a client receives for a given host name.
- Test with `curl` and `openssl s_client` that the certificate is trusted for the matching name and rejected for another name.
