---
draft: true
exam_objectives:
- Properly set up Ingress with TLS
---
# Build TLS With openssl For Traefik

The typical exam task for TLS on an Ingress has the same shape each time: create a private key and a certificate with `openssl`, store them in a Kubernetes TLS Secret, add a `tls` section to the Ingress, and prove with a client that the right certificate is served. Each step has a small mistake that makes the whole chain fail, and the failure usually shows as a generic certificate error on the client.

This module drills the complete flow with Traefik. It explains what a certificate must contain, creates a self-signed certificate and a certificate signed by your own certificate authority, builds the TLS Secret, connects it to an Ingress and verifies the result from the client side. It ends with the redirect from HTTP to HTTPS and with the certificate that Traefik serves when something is wrong.

## Learning objectives

After this module you can:

- Create a private key and a self-signed certificate with a Subject Alternative Name using `openssl req -x509`.
- Create a certificate authority and a server certificate signed by it, and verify the chain with `openssl verify`.
- Create a `kubernetes.io/tls` Secret with `kubectl create secret tls` and check that the key and the certificate match.
- Add `spec.tls` to a Traefik Ingress and verify the served certificate with `curl --cacert --resolve` and `openssl s_client`.
- Redirect HTTP to HTTPS in Traefik and explain what the default certificate means.

## Before you start

You need Kubernetes basics: Deployments, Services, Secrets and `kubectl`. You also need `curl` and OpenSSL 1.1.1 or newer on your own machine. The `openssl` that comes with some macOS versions is LibreSSL and does not support every option used here, so check `openssl version` first. The module has six parts: certificate fundamentals, a self-signed certificate, a certificate signed by your own authority, the TLS Secret, the TLS Ingress and its verification, and the redirect with the default certificate. A graded lab follows the fifth and the sixth part.

Your playground is a `kind` cluster running Kubernetes v1.35 with Traefik installed. It has these objects:

| Namespace | Object | What it is |
| --- | --- | --- |
| `starfleet` | `probe` and `scout` Deployments and Services | Web servers on pod port 8080, Service port 80; each answers with its own `app` name |
| `outpost` | `beacon` Deployment and Service | A third web server in a different namespace |
| `starfleet` | `shuttle` pod | A `busybox` pod for requests from inside the cluster |
| `ingress-system` | `traefik` Deployment and Service | The Ingress controller; Service port 80 for HTTP, 443 for HTTPS |
| `ingress-system` | `traefik-dynamic` ConfigMap | The file configuration of Traefik, with a minimum TLS version of 1.2 |

No TLS Secret exists yet. `kubectl` already points at the playground cluster. Launch your playground now and keep it running while you read:

<!-- astrona:playground -->
