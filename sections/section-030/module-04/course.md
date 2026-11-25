# Harden And Troubleshoot Traefik TLS

A TLS Ingress that works is not yet a safe one. TLS (Transport Layer Security) is the protocol that encrypts the connection between a client and a server. An Ingress is the Kubernetes object that routes outside requests for a host name to a Service in the cluster. An Ingress can serve TLS and still be weak.

The Ingress controller is the program that reads Ingress objects and handles the real connections. It may still accept old protocol versions, serve a certificate for any name, read every Secret in the cluster and expose an API without a password. When something breaks, a client often sees the same error for very different causes. A security specialist has to set the TLS policy, require client certificates where needed, reduce what the controller can reach, replace certificates before they expire, and trace a failure to its cause.

This module uses Traefik as the Ingress controller, on a `kind` cluster. Traefik reads its TLS policy from a dynamic configuration file, which comes from a ConfigMap. So the module needs no custom resource definitions (CRDs), the extra object kinds that some controllers add to the Kubernetes API.

## What you will learn

After this module, you can:

- require a minimum TLS version and strict server name matching, and prove the policy with `openssl s_client`;
- require and verify client certificates with a certificate authority (CA), and test a request with and without a client certificate;
- name the permissions and open ports that make up the attack surface of the controller, and check each one with `kubectl`;
- replace and rotate a certificate in a Secret, and confirm the new serial number and end date on the wire;
- find why a TLS Ingress fails: a missing Secret, a certificate and key that do not belong together, a wrong host or a wrong class.

## How the module is laid out

You start with **TLS Versions, Ciphers And Server Names**, which sets the TLS policy that every route uses. **Mutual TLS With Client Certificates** then makes one route ask each client for a certificate. **Shrink The Controller Attack Surface** looks at the controller itself: what it can read, what it exposes and how it runs. **Rotate And Replace Certificates** swaps an expiring certificate and proves that the new one is served. **Troubleshoot TLS Ingress Failures** closes the module with a fixed order of checks and four broken routes to repair.

A lab follows each part, so you can practise the skill right away.

## Before you start

You should know how to create a certificate and a private key with `openssl`, and how to store them in a Kubernetes Secret of type `kubernetes.io/tls`. You should also know the Kubernetes basics: pods, namespaces, Services, Ingress objects and `kubectl get`, `kubectl apply` and `kubectl describe`. You need `openssl` and `curl` on your own machine.

## Your playground

Your playground is a `kind` cluster that runs Kubernetes v1.35 with Traefik v3.6.1 installed. The cluster already holds these objects:

| Namespace | Object | What it is |
| --- | --- | --- |
| `starfleet` | `probe` and `scout` Deployments, one pod each | Small web servers that listen on port 8080 |
| `starfleet` | `probe` and `scout` Services | Port 80, forwards to port 8080 of the pods |
| `starfleet` | `shuttle` pod, label `app: shuttle` | A client pod with `busybox` |
| `starfleet` | Ingress `probe` with Secret `probe-tls` | A working TLS route for `probe.example.test`; the certificate is valid for one day |
| `starfleet` | Ingresses `case-one` to `case-four` | Four TLS routes that do not work yet |
| `starfleet` | Secrets `one-cert`, `two-tls`, `three-tls` and `four-tls` | The TLS Secrets that belong to the four broken routes |
| `ingress-system` | `traefik` Deployment, Service and ServiceAccount | The controller; the Service publishes port 80 and port 443 |
| `ingress-system` | ConfigMap `traefik-dynamic` | The dynamic configuration file with the TLS options; it sets `minVersion: VersionTLS12` |
| cluster-wide | ClusterRole and ClusterRoleBinding `traefik`, IngressClass `traefik` | The permissions of the controller and the class it serves |
| `outpost` | (empty) | A second namespace with no workloads |

`kubectl` already points at the playground cluster. Start your playground now and keep it running while you read:

<!-- astrona:playground -->
