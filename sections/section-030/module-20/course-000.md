# Run Traefik On kind

An Ingress controller is the program that turns Ingress rules into working routes for web requests. When the controller is missing, set up wrong, or not linked to the Ingress by its class, no request is routed. The Kubernetes API still gives no error, so the problem is easy to miss.

A security specialist must be able to read how a controller is installed, send test requests to it and read its logs. Every later step with TLS (Transport Layer Security, the encryption behind HTTPS) depends on a controller that works.

This module uses Traefik. Exam environments may use another controller. The Ingress API is the same for all of them, so the rules you write here work with any controller that serves the class you name.

## What you will learn

After this module, you can:

- describe how Traefik turns an Ingress into a router, a service and a pod address, and say which part does each step;
- read the Traefik Deployment, Service, IngressClass and RBAC (role-based access control) objects and explain what each one does;
- create an Ingress with `ingressClassName: traefik` and test it with `curl` and a `Host` header;
- use the `Prefix` and `Exact` path types, route several Services from one host, and set a default backend;
- read the Traefik log, the access log and the API to see which route handled a request.

## How the module is laid out

You start with **Ingress Controller Architecture With Traefik**, which explains the objects, the Traefik words and the path of one request. It has no commands. **Read The Traefik Installation On kind** then reads the installed objects one by one. **First Ingress And Host Header Testing** creates the first route and tests it from your machine.

**Path Types And Priority** shows how Traefik chooses between rules that overlap. **Several Services And A Default Backend** publishes two Services on one host and catches every request that no rule matches. **Inspect The Running Controller** closes the module by reading the evidence that Traefik itself records.

A graded lab follows each part that has commands, so you can practise the skill right away.

## Before you start

You should know the Kubernetes basics: Deployments, Services and `kubectl`. You also need `curl` on your own machine.

## Your playground

Your playground is a `kind` cluster that runs Kubernetes v1.35 with Traefik already installed. The cluster already has these objects:

| Namespace | Object | What it is |
| --- | --- | --- |
| `starfleet` | `probe` Deployment and Service, label `app: probe` | A small web server on pod port 8080, Service port 80; it answers with `app=probe`, the pod name, the path and the host |
| `starfleet` | `scout` Deployment and Service, label `app: scout` | The same web server, it answers with `app=scout` |
| `starfleet` | `web-code` ConfigMap | The Python code that both web servers run |
| `starfleet` | `shuttle` pod, label `app: shuttle` | A `busybox` pod for requests from inside the cluster |
| `outpost` | (no workloads) | A spare namespace |
| `ingress-system` | `traefik` Deployment, Service and ServiceAccount | The Ingress controller; Service port 80 for HTTP, 443 for HTTPS, 8080 for the API and dashboard |
| (cluster-wide) | `traefik` ClusterRole and ClusterRoleBinding | The read permissions of the `traefik` ServiceAccount |
| (cluster-wide) | `traefik` IngressClass | Tells Ingress objects which controller handles them |

`kubectl` already points at the playground cluster. Start your playground now and keep it running while you read:

<!-- astrona:playground -->
