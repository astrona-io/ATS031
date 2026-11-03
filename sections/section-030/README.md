---
draft: true
exam_objectives:
- Properly set up Ingress with TLS
---
# Properly set up Ingress with TLS

A client requests `probe.example.test` over HTTPS. Traefik picks the route, presents a certificate and forwards the request to the `probe` Service. The Ingress object only declares the rules; the controller does the work, and the client decides whether to trust the certificate. This section teaches routing, the Traefik installation, certificates made with `openssl`, the TLS Secret, the TLS policy of the controller and the checks that prove the right certificate is served.

## Learning Path

1. Set Up Ingress With TLS: routing by controller, class, host and path, the TLS Secret and a first verified TLS Ingress, with one graded lab.
2. Run Traefik On kind: controller architecture, the installation objects, host header testing, path types and priority, several Services with a default backend, and inspection of the running controller. A graded lab routes two Services from one host.
3. Build TLS With openssl For Traefik: certificate fundamentals, self-signed and CA-signed certificates, the TLS Secret, `spec.tls` with verification, the HTTPS redirect, HSTS and the default certificate. Two graded labs create a TLS route and repair a broken one.
4. Harden And Troubleshoot Traefik TLS: TLS versions and strict server names, mutual TLS, the attack surface of the controller, certificate rotation and a fixed order of checks for failures. Two graded labs set the TLS policy and repair four broken Ingresses.
5. Capstone: publish two hosts over HTTPS with their own certificates, a redirect to HTTPS and TLS 1.3, and repair a broken Ingress in one cluster.

Each module ends with a summary and a ten-question knowledge check. Each lab follows the part that practises its skill. Every module has a playground, a private `kind` cluster with Kubernetes v1.35; launch it from the landing page and keep it running while you read.

## Learning Outcomes

- Explain the roles of the Ingress object, the IngressClass and the Ingress controller.
- Read a Traefik installation on `kind` and test a route with a `Host` header.
- Write Ingress rules with host, path, `pathType` and a backend Service port.
- Create a self-signed certificate and a CA-signed certificate with a Subject Alternative Name using `openssl`.
- Create a `kubernetes.io/tls` Secret from a certificate and a key, and check that the two match.
- Configure `spec.tls` and prove with `curl` and `openssl s_client` that the certificate is trusted for the matching name and rejected for another name.
- Redirect HTTP to HTTPS and explain HSTS and the default certificate.
- Set a minimum TLS version, strict server names and client certificate checks in the Traefik TLS options.
- Describe the attack surface of the Ingress controller and rotate a certificate with evidence.
- Troubleshoot a TLS Ingress in a fixed order: class, Secret, key pair, host and SAN, and controller log.
