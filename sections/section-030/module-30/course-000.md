# Build TLS With openssl For Traefik

Transport Layer Security (TLS) is the protocol that encrypts a connection and lets the client check who the server is. HTTPS is HTTP sent over TLS. An exam task about TLS on an Ingress has the same shape almost every time. You create a private key and a certificate with `openssl`, store them in a Kubernetes TLS Secret, add a `tls` section to the Ingress, and prove with a client that the right certificate comes back.

Each of these steps has a small mistake that breaks the whole chain. The client then shows only a general certificate error, which does not say which step went wrong. So it pays to know what each step does and how to check it.

This module works through the full flow with Traefik, the Ingress controller in your playground. An Ingress controller is the program that reads Ingress objects and routes outside requests to Services. Traefik also holds the certificates and answers the TLS handshake.

## What you will learn

After this module, you can:

- create a private key and a self-signed certificate with a Subject Alternative Name, using `openssl req -x509`;
- create a certificate authority and a server certificate that it signs, and verify the chain with `openssl verify`;
- create a `kubernetes.io/tls` Secret with `kubectl create secret tls` and check that the key and the certificate belong together;
- add `spec.tls` to a Traefik Ingress and check the served certificate with `curl --cacert --resolve` and `openssl s_client`;
- redirect HTTP to HTTPS in Traefik and explain what the default certificate means.

## How the module is laid out

You start with **Certificate Fundamentals Needed For The Exam**, which explains what a certificate contains and which checks a client runs. It has no commands. **Self-Signed Certificate With openssl** then builds a certificate that signs itself, and **Sign A Server Certificate With Your Own CA** creates a small certificate authority that signs a server certificate.

With the files ready, **Create The TLS Secret** stores them in the cluster in the form Traefik reads. **Configure spec.tls And Verify** connects the Secret to an Ingress and tests it from the client side. **HTTPS Redirect, HSTS And The Default Certificate** closes the module with the redirect from HTTP to HTTPS, the HSTS header and the certificate Traefik serves for unknown names.

A graded lab follows each part except the first, so you can practise the skill right away.

## Before you start

You should know the Kubernetes basics: Deployments, Services, Secrets and `kubectl`. You also need `curl` and OpenSSL 1.1.1 or newer on your own machine.

Some macOS versions ship LibreSSL under the name `openssl`. LibreSSL does not support every option this module uses, so run `openssl version` first and check which one you have.

## Your playground

Your playground is a `kind` cluster that runs Kubernetes v1.35 with Traefik v3.6.1 installed. No TLS Secret exists yet. The cluster already runs these objects:

| Namespace | Object | What it is |
| --- | --- | --- |
| `starfleet` | `probe` Deployment, one pod, label `app: probe` | A small web server on port 8080 that answers with `app=probe` and its pod name |
| `starfleet` | `probe` Service | Port 80, forwards to port 8080 of the `probe` pod |
| `starfleet` | `scout` Deployment, one pod, label `app: scout` | A second web server on port 8080 that answers with `app=scout` |
| `starfleet` | `scout` Service | Port 80, forwards to port 8080 of the `scout` pod |
| `starfleet` | `shuttle` pod, label `app: shuttle` | A `busybox` client pod for requests from inside the cluster |
| `outpost` | `beacon` Deployment, one pod, label `app: beacon` | A third web server on port 8080, in another namespace |
| `outpost` | `beacon` Service | Port 80, forwards to port 8080 of the `beacon` pod |
| `ingress-system` | `traefik` Deployment | The Ingress controller, with the entrypoint `web` on port 8000 and `websecure` on port 8443 |
| `ingress-system` | `traefik` Service | Port 80 for HTTP and port 443 for HTTPS, forwards to the two entrypoints |
| `ingress-system` | `traefik-dynamic` ConfigMap | The file configuration of Traefik, with a minimum TLS version of 1.2 |
| cluster-wide | `traefik` IngressClass | Links Ingress objects with `ingressClassName: traefik` to Traefik |

The `starfleet` and `outpost` namespaces each also hold a `web-code` ConfigMap with the code of the web servers.

`kubectl` already points at the playground cluster. Start your playground now and keep it running while you read:

<!-- astrona:playground -->
