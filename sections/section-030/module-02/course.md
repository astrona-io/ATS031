---
draft: true
exam_objectives:
- Properly set up Ingress with TLS
---
# Run Traefik On kind

An Ingress controller is the program that turns Ingress rules into running routes. When it is missing, misconfigured or not matched to the Ingress by class, no request is routed, and the Kubernetes API gives no error. A security specialist must be able to read how a controller is installed, send test requests to it and read its logs, because every later step with TLS depends on a controller that works.

This module uses Traefik, the same controller as the rest of this section. It explains how Traefik is built, reads the objects that make up its installation on a `kind` cluster, and routes plain HTTP by host and path. Exam environments may use another controller, but the Ingress API is the same, so the rules you write here work with any controller that serves the class you name.

## Learning objectives

After this module you can:

- Describe how Traefik turns an Ingress into a router, a service and a pod address, and which part does each step.
- Read the Traefik Deployment, Service, IngressClass and RBAC objects and explain what each one does.
- Create an Ingress with `ingressClassName: traefik` and test it with `curl` and a `Host` header.
- Use the `Prefix` and `Exact` path types, route several Services from one host, and set a default backend.
- Read the Traefik logs, the access log and the API to see which route handled a request.

## Before you start

You need Kubernetes basics: Deployments, Services and `kubectl`. You also need `curl` on your own machine. The module has six parts: controller architecture, the installation on `kind`, a first Ingress, path types and priority, several Services with a default backend, and inspection of the running controller. The graded lab follows the part on several Services.

Your playground is a `kind` cluster running Kubernetes v1.35 with Traefik already installed. It has these objects:

| Namespace | Object | What it is |
| --- | --- | --- |
| `starfleet` | `probe` and `scout` Deployments and Services | Web servers on pod port 8080, Service port 80; each answers with its own `app` name |
| `starfleet` | `shuttle` pod | A `busybox` pod for requests from inside the cluster |
| `ingress-system` | `traefik` Deployment and Service | The Ingress controller; Service port 80 for HTTP, 443 for HTTPS, 8080 for the API and dashboard |
| (cluster-wide) | `traefik` IngressClass | Tells Ingress objects which controller handles them |

`kubectl` already points at the playground cluster. Launch your playground now and keep it running while you read:

<!-- astrona:playground -->
