---
draft: true
exam_objectives:
- Properly set up Ingress with TLS
---
# Harden And Troubleshoot Traefik TLS

A TLS Ingress that works is not yet a safe one. The controller may still accept old protocol versions, serve a certificate for any name, hold a read permission on every Secret in the cluster and expose an API without a password. When something breaks, the symptom a client sees is often the same for very different causes. A security specialist has to set the TLS policy, require client certificates where needed, reduce what the controller can reach, replace certificates before they expire, and trace a failure to its cause.

This module uses Traefik on `kind`, like the rest of this section. The TLS policy lives in a dynamic configuration file that Traefik reads from a ConfigMap, so no custom resource definitions are needed.

## Learning objectives

After this module you can:

- Require a minimum TLS version and strict server name matching, and prove the policy with `openssl s_client`.
- Require and verify client certificates with a CA, and test with and without a client certificate.
- Name the permissions and open ports that make up the attack surface of the controller and check them with `kubectl`.
- Replace and rotate a certificate in a Secret and confirm the new serial and end date on the wire.
- Diagnose a failing TLS Ingress from a missing Secret, a mismatched pair, a wrong host or a wrong class.

## Before you start

You need the TLS basics from creating certificates and TLS Secrets, plus `openssl` and `curl` on your own machine. The module has five parts: TLS versions and server names, mutual TLS, the attack surface of the controller, certificate rotation, and troubleshooting. The first graded lab follows the first part, and the second follows the troubleshooting part.

Your playground is a `kind` cluster running Kubernetes v1.35 with Traefik installed and these objects:

| Namespace | Object | What it is |
| --- | --- | --- |
| `starfleet` | `probe` and `scout` Deployments and Services | Web servers behind Service port 80 |
| `starfleet` | Ingress `probe` with Secret `probe-tls` | A working TLS route for `probe.example.test`; the certificate is valid for one day |
| `starfleet` | Ingresses `case-one` to `case-four` | Four routes that do not work yet |
| `ingress-system` | `traefik` Deployment and Service | The controller; it reads the ConfigMap `traefik-dynamic` for TLS options |

`kubectl` already points at the playground cluster. Launch your playground now and keep it running while you read:

<!-- astrona:playground -->
