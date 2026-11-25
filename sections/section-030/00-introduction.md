# Properly set up Ingress with TLS

A client asks for `probe.example.test` over HTTPS. Something must pick the right route, show a certificate and pass the request on to the `probe` Service. The client then decides whether it trusts that certificate. If any of these steps is wrong, the connection fails, or worse, it works with a certificate nobody should trust.

An Ingress is the Kubernetes object that declares these routes. It only describes the rules. A separate program, the Ingress controller, does the work. In this course the controller is Traefik. In this section, you learn how routing works, how to make certificates with `openssl`, how to store them in a TLS Secret, and how to prove that the right certificate is served.

## What you will learn

The section moves from a first route to a hardened controller:

- **Set Up Ingress With TLS.** Routing by controller, class, host and path, the TLS Secret, a first verified TLS Ingress, and several hosts that each have their own certificate.
- **Run Traefik On kind.** How the controller is built and installed, how to test a host name with a header, path types and priority, several Services with a default backend, and how to inspect the running controller.
- **Build TLS With openssl For Traefik.** Certificate basics, self-signed and CA-signed certificates, the TLS Secret, `spec.tls` with verification, the HTTPS redirect, HSTS and the default certificate.
- **Harden And Troubleshoot Traefik TLS.** TLS versions and strict server names, mutual TLS, the attack surface of the controller, certificate rotation and a fixed order of checks when a route fails.

## How this section works

Each module has its own playground: a private `kind` cluster that runs Kubernetes v1.35. Start it from the first page of the module and keep it running while you read, because every page has commands to try.

When a page teaches a skill you can be graded on, a lab comes right after it. A lab gives you a short task in a fresh cluster and checks your result. Each module ends with a summary and a short knowledge check.

## By the end of this section

You will be able to:

- explain the roles of the Ingress object, the IngressClass and the Ingress controller;
- read a Traefik installation on `kind` and test a route with a `Host` header;
- write Ingress rules with a host, a path, a `pathType` and a backend Service port;
- create a self-signed certificate and a CA-signed certificate with a Subject Alternative Name (SAN) using `openssl`;
- create a `kubernetes.io/tls` Secret from a certificate and a key, and check that the two match;
- configure `spec.tls` and prove with `curl` and `openssl s_client` that the certificate is trusted for the matching name and rejected for another name;
- redirect HTTP to HTTPS, and explain HSTS and the default certificate;
- set a minimum TLS version, strict server names and client certificate checks in the Traefik TLS options;
- describe the attack surface of the Ingress controller and rotate a certificate with evidence;
- troubleshoot a TLS Ingress in a fixed order: class, Secret, key pair, host and SAN, then the controller log.
