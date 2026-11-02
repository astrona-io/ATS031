---
draft: true
exam_objectives:
- Properly set up Ingress with TLS
---
# Set Up Ingress With TLS

An Ingress is a Kubernetes object that routes HTTP and HTTPS requests from outside the cluster to Services inside it, using the host name and the URL path of the request. Without TLS, every request and response crosses the network in clear text, and a client cannot know whether it talks to the intended server. Transport Layer Security (TLS) encrypts the connection and lets the client verify the identity of the server with a certificate.

An Ingress object does nothing by itself. A separate program, the Ingress controller, watches Ingress objects and does the routing. In this module the controller is Traefik. The controller also terminates TLS: it holds the certificate and private key, which the Ingress takes from a Kubernetes Secret, and it forwards the decrypted request to the Service.

This module teaches you to route by host and path, to create a TLS Secret from a certificate and key, to configure an Ingress that uses it, and to prove with real requests that the right certificate is served and a wrong host name is rejected.

## Learning objectives

After this module you can:

- Explain the roles of the Ingress object, the IngressClass and the Ingress controller.
- Write Ingress rules with host, path, `pathType` and a backend Service port.
- Create a `kubernetes.io/tls` Secret from a certificate and a key, and check that the two match.
- Configure `spec.tls` in an Ingress and explain which certificate a client receives for a given host name.
- Test with `curl` and `openssl s_client` that the certificate is trusted for the matching name and rejected for another name.

## Before you start

You need Kubernetes basics: Deployments, Services, Secrets and `kubectl`. You also need `curl` and `openssl` on your own machine. The module has four parts. The first covers routing. The second covers certificates and the TLS Secret. The third configures the TLS Ingress. The fourth covers several hosts, the certificate choice by server name, and troubleshooting.

Your playground is a `kind` cluster running Kubernetes v1.35. It has these objects:

| Namespace | Object | What it is |
| --- | --- | --- |
| `starfleet` | `probe` Deployment (two pods) and `probe` Service | A web server on pod port 8080, Service port 80 |
| `starfleet` | `probe-tls` Secret | A self-signed certificate and key for the host name `probe.local` |
| `ingress-system` | `traefik` Deployment and Service | The Ingress controller; Service port 80 for HTTP and 443 for HTTPS |
| (cluster-wide) | `traefik` IngressClass | Tells Ingress objects which controller handles them |

`kubectl` already points at the playground cluster. Launch your playground now and keep it running while you read:

<!-- astrona:playground -->
