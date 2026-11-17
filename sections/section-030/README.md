---
exam_objectives:
- Properly set up Ingress with TLS
---
# Properly set up Ingress with TLS

A client requests `probe.example.test` over HTTPS. Traefik picks the route, presents a certificate and forwards the request to the `probe` Service. The Ingress object only declares the rules; the controller does the work, and the client decides whether to trust the certificate. This section teaches routing, the Traefik installation, certificates made with `openssl`, the TLS Secret, the TLS policy of the controller and the checks that prove the right certificate is served.

## Learning Path

1. Set Up Ingress With TLS: routing by controller, class, host and path, the TLS Secret, a first verified TLS Ingress and several hosts with their own certificates. Four graded labs repair a route, create a TLS Secret, verify a TLS Ingress and serve two hosts.
2. Run Traefik On kind: controller architecture, the installation objects, host header testing, path types and priority, several Services with a default backend, and inspection of the running controller. Five graded labs repair the installation, publish a Service by host name, match Exact and Prefix paths, route two Services from one host and find a broken route with the Traefik API.
3. Build TLS With openssl For Traefik: certificate fundamentals, self-signed and CA-signed certificates, the TLS Secret, `spec.tls` with verification, the HTTPS redirect, HSTS and the default certificate. Five graded labs create a self-signed certificate, sign one with a CA, repair a missing Secret, create a TLS route, and add the redirect with HSTS.
4. Harden And Troubleshoot Traefik TLS: TLS versions and strict server names, mutual TLS, the attack surface of the controller, certificate rotation and a fixed order of checks for failures. Five graded labs set the TLS policy, require client certificates, close the Traefik API, rotate a certificate and repair four broken Ingresses.

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
